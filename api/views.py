from django.http import JsonResponse
from .models import Post, Author
from django.db.models import Count, Sum, F, Window
import json

def posts_naive(request):
    posts = Post.objects.all()
    data = []
    for post in posts:
        data.append({
            "id": post.id,
            "title": post.title,
            "author_name": post.author.name,
            "comment_count": post.comments.count()
        })
    return JsonResponse(data, safe=False)

def posts_optimized(request):
    posts = Post.objects.select_related('author').annotate(comment_count=Count('comments'))
    data = []
    for post in posts:
        data.append({
            "id": post.id,
            "title": post.title,
            "author_name": post.author.name,
            "comment_count": post.comment_count
        })
    return JsonResponse(data, safe=False)

def posts_advanced(request):
    # We want total_author_views which is the sum of views of all posts by the same author.
    # We use a Window function with Sum('views') partitioned by 'author_id'.
    # Since we are querying Post, the partition_by will be the author_id of the Post.
    
    # Wait, the prompt says: 
    # Window(expression=Sum('author__posts__views'), partition_by=[F('author_id')])
    # Actually if we query Post, Sum('views') partitioned by author_id sums the views of the posts in the current table over the partition.
    
    # Wait, if we use annotate(total_author_views=Window(expression=Sum('views'), partition_by=[F('author_id')])),
    # does that interfere with Count('comments')? Let's check. Window functions and Group By (used by Count) can sometimes clash.
    # To be safe from grouping issues, we can use a Subquery.
    # The prompt allows either: "using a window function or subquery".
    # Subquery is usually simpler to get right in Django without GROUP BY conflicts.
    
    from django.db.models import Subquery, OuterRef
    
    # Using Subquery:
    author_views_sq = Post.objects.filter(author_id=OuterRef('author_id')).values('author_id').annotate(total_views=Sum('views')).values('total_views')
    
    posts = Post.objects.select_related('author').annotate(
        comment_count=Count('comments'),
        total_author_views=Subquery(author_views_sq)
    )
    
    data = []
    for post in posts:
        data.append({
            "id": post.id,
            "title": post.title,
            "author_name": post.author.name,
            "comment_count": post.comment_count,
            "total_author_views": post.total_author_views or 0
        })
    return JsonResponse(data, safe=False)
