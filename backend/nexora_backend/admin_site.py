from django.conf import settings
from unfold.sites import UnfoldAdminSite

class NexoraAdminSite(UnfoldAdminSite):
    site_header = "Nexora Premium Admin"
    site_title = "Nexora Admin"
    index_title = "Boshqaruv paneliga xush kelibsiz"

admin_site = NexoraAdminSite(name="admin")
