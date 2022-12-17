from main import app
import pytest
import sqlalchemy


class TestViews:
    def setup(self):
        app.testing = True
        self.client = app.test_client()

    @pytest.mark.parametrize('a', [('/home'), ('/videos'), ('/download_video')])
    def test_home(self, a):
        res = self.client.get(a)
        assert res.status_code == 200


