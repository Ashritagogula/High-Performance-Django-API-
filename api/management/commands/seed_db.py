from django.core.management.base import BaseCommand
from api.models import Author, Post, Comment
from faker import Faker
import random

class Command(BaseCommand):
    help = 'Seeds the database with Authors, Posts, and Comments for benchmarking'

    def handle(self, *args, **kwargs):
        fake = Faker()
        
        self.stdout.write('Deleting old data...')
        Comment.objects.all().delete()
        Post.objects.all().delete()
        Author.objects.all().delete()

        self.stdout.write('Creating new data...')
        
        authors = []
        for _ in range(20):
            authors.append(Author(name=fake.name(), bio=fake.text()))
        Author.objects.bulk_create(authors)
        authors = list(Author.objects.all())

        posts = []
        for author in authors:
            for _ in range(10):
                posts.append(Post(
                    author=author,
                    title=fake.sentence(),
                    content=fake.text(),
                    views=random.randint(0, 1000)
                ))
        Post.objects.bulk_create(posts)
        posts = list(Post.objects.all())

        comments = []
        for post in posts:
            for _ in range(10):
                comments.append(Comment(
                    post=post,
                    author_name=fake.name(),
                    body=fake.sentence()
                ))
        # Batch create comments as it might be large
        Comment.objects.bulk_create(comments, batch_size=500)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded: 20 Authors, 200 Posts, 2000 Comments.'))
