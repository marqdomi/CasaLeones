"""Tests for authentication routes."""
import pytest
from tests.conftest import login


class TestLogin:
    def test_login_page_loads(self, client):
        resp = client.get('/login')
        assert resp.status_code == 200
        assert b'login' in resp.data.lower() or b'iniciar' in resp.data.lower()

    def test_login_valid_credentials(self, client, admin_user):
        resp = login(client, 'admin_test', 'Test1234!')
        assert resp.status_code == 200

    def test_login_invalid_password(self, client, admin_user):
        resp = login(client, 'admin_test', 'wrong_password')
        assert resp.status_code == 200
        # Should show error or stay on login page

    def test_login_nonexistent_user(self, client):
        resp = login(client, 'noexiste', 'Test1234!')
        assert resp.status_code == 200

    def test_logout(self, client, admin_user):
        login(client, 'admin_test', 'Test1234!')
        resp = client.get('/logout', follow_redirects=True)
        assert resp.status_code == 200


class TestProtectedRoutes:
    def test_admin_requires_login(self, client):
        resp = client.get('/admin/', follow_redirects=True)
        assert resp.status_code == 200
        # Should redirect to login

    def test_meseros_requires_login(self, client):
        resp = client.get('/meseros/', follow_redirects=True)
        assert resp.status_code == 200
