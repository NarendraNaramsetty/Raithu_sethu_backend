"""
seed_community — intentionally disabled.

All fake/demo data has been removed. The community is now driven entirely by
real farmer posts created through the authenticated API.

This command is kept as a no-op stub so existing scripts that reference it
do not break. It will never insert fake posts.
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'No-op stub — fake seed data has been permanently removed.'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING(
                'seed_community: nothing to do. '
                'The community is populated only by real farmer posts via the API.'
            )
        )
