from datetime import datetime
from functools import partial

from dashboards.readouts import UnreviewedReadout
from sumo.tests import TestCase
from wiki.tests import revision, translated_revision


NON_DEFAULT_LOCALE = 'de'
translated_revision = partial(translated_revision, locale=NON_DEFAULT_LOCALE)


class MockRequest(object):
    locale = NON_DEFAULT_LOCALE


class UnreviewedChangesTests(TestCase):
    """Tests for the Unreviewed Changes readout

    I'm not trying to cover every slice of the Venn diagram--just the tricky
    bits.

    """

    fixtures = ['users.json']

    @staticmethod
    def titles():
        """Return the titles shown by the Unreviewed Changes readout."""
        return [row['title'] for row in
            UnreviewedReadout(MockRequest()).rows()]

    def test_unrevieweds_after_current(self):
        """Show the unreviewed revisions with later creation dates than the
        current"""
        current = translated_revision(is_approved=True,
                                      created=datetime(2000, 1, 1))
        current.save()
        unreviewed = revision(document=current.document,
                              created=datetime(2000, 2, 1))
        unreviewed.save()
        assert unreviewed.document.title in self.titles()

    def test_current_revision_null(self):
        """Show all unreviewed revisions if none have been approved yet."""
        unreviewed = translated_revision()
        unreviewed.save()
        assert unreviewed.document.title in self.titles()

    def test_rejected_newer_than_current(self):
        """If there are reviewed but unapproved (i.e. rejected) revisions newer
        than the current_revision, don't show them."""
        rejected = translated_revision(reviewed=datetime.now())
        rejected.save()
        assert rejected.document.title not in self.titles()
