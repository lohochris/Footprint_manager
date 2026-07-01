from locust import HttpUser, task, between
import os, time

class APIUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        response = self.client.post('/api/auth/token/', json={
            'username': os.getenv('PERF_TEST_USER', 'testuser'),
            'password': os.getenv('PERF_TEST_PASS', 'testpass')
        })
        self.token = response.json().get('access') if response.status_code == 200 else None

    def auth_headers(self):
        return {'Authorization': f'Bearer {self.token}'} if self.token else {}

    @task(2)
    def list_organizations(self):
        self.client.get('/api/organizations/', headers=self.auth_headers())

    @task(1)
    def create_organization(self):
        payload = {
            'name': 'Perf Org',
            'slug': f'perf-org-{int(time.time())}',
            'description': 'Performance test organization'
        }
        self.client.post('/api/organizations/', json=payload, headers=self.auth_headers())

    @task(2)
    def list_workspaces(self):
        self.client.get('/api/workspaces/', headers=self.auth_headers())

    @task(1)
    def create_workspace(self):
        payload = {
            'name': 'Perf Workspace',
            'slug': f'perf-ws-{int(time.time())}',
            'organization': 1
        }
        self.client.post('/api/workspaces/', json=payload, headers=self.auth_headers())

    @task(1)
    def membership_flow(self):
        self.client.get('/api/workspaces/1/members/', headers=self.auth_headers())
        add_payload = {'user': 2, 'role': 'member'}
        self.client.post('/api/workspaces/1/members/', json=add_payload, headers=self.auth_headers())
        self.client.delete('/api/workspaces/1/members/2/', headers=self.auth_headers())

    @task(1)
    def invitation_flow(self):
        payload = {'email': 'invitee@example.com', 'workspace': 1}
        resp = self.client.post('/api/invitations/', json=payload, headers=self.auth_headers())
        if resp.status_code == 201:
            invitation_id = resp.json().get('id')
            self.client.post(f'/api/invitations/{invitation_id}/accept/', headers=self.auth_headers())

    @task(1)
    def ownership_transfer(self):
        payload = {'new_owner': 2}
        self.client.post('/api/organizations/1/transfer-ownership/', json=payload, headers=self.auth_headers())

    @task(1)
    def archive_restore(self):
        self.client.post('/api/organizations/1/archive/', headers=self.auth_headers())
        self.client.post('/api/organizations/1/restore/', headers=self.auth_headers())
