from django.conf import settings
from unfold.sites import UnfoldAdminSite

class RankEduAdminSite(UnfoldAdminSite):
    site_header = "RankEdu Premium Admin"
    site_title = "RankEdu Admin"
    index_title = "Boshqaruv paneliga xush kelibsiz"

admin_site = RankEduAdminSite(name="admin")
