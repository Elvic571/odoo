import requests
import json
from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError

class PacksizeApiService(models.AbstractModel):
    _name = 'packsize.api.service'
    _description = 'Packsize API Service'

    def _get_stored_token(self):
        """Get stored token and expiration from ir.config_parameter"""
        params = self.env['ir.config_parameter'].sudo()
        token = params.get_param('packsize_api.token')
        expiration_str = params.get_param('packsize_api.token_expiration')
        if token and expiration_str:
            expiration = datetime.fromisoformat(expiration_str)
            if datetime.utcnow() < expiration:
                return token
        return None

    def _store_token(self, token, expires_in_seconds):
        """Store token and expiration in ir.config_parameter"""
        expiration = datetime.utcnow() + timedelta(seconds=expires_in_seconds)
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('packsize_api.token', token)
        params.set_param('packsize_api.token_expiration', expiration.isoformat())

    def _request_new_token(self, packsize_ip, username, password, client_id, client_secret):
        """Request and store new token"""
        token_url = f"http://{packsize_ip}/IdentityApi/api/v1/oauth/token"
        data = {
            'grant_type': 'password',
            'username': username,
            'password': password,
            'client_id': client_id,
            'client_secret': client_secret
        }
        response = requests.post(token_url, data=data, timeout=10)
        response.raise_for_status()
        result = response.json()
        token = result.get('access_token')
        expires_in = result.get('expires_in', 86400)  # fallback 24h
        if not token:
            raise UserError("No access token returned from Packsize.")
        self._store_token(token, expires_in)
        return token

    @api.model
    def send_packsize_job(self, length, width, height, quantity,
                          operator, datetime_str, mo_number,
                          product_barcode, sku,
                          test_mode=False):
        """
        Send job to Packsize machine.
        If test_mode=True, send to webhook.site without token.
        """
        # ------------------
        # Configurations
        # ------------------

        packsize_ip = "23.244.22.74:3530"
        username = "YOUR_USERNAME"
        password = "YOUR_PASSWORD"
        client_id = "Default client_id"
        client_secret = "Default client_secret"
        design_id = "2010013"
        production_group_name = "PG1"

        # ------------------
        # Test mode
        # ------------------
        if test_mode:
            api_url = "https://webhook.site/ab7ee08a-7118-408e-8dc1-cb8a1434af17"
            headers = {}

        else:
            api_url = f"http://{packsize_ip}/importerapi/api/v1/ImportData"
            token = self._get_stored_token()
            if not token:
                token = self._request_new_token(packsize_ip, username, password, client_id, client_secret)
            headers = {'Authorization': f'Bearer {token}'}

        # ------------------
        # Send job
        # ------------------
        job_data = [{
            "Title": mo_number,
            "Width": str(width),
            "Length": str(length),
            "Height": str(height),
            "Quantity": str(quantity),
            "Operator": str(operator),
            "DateTime": str(datetime_str),
            "Barcode": str(product_barcode),
            "SKU": str(sku),
            "DesignId": design_id,
            "ProductionGroupName": production_group_name
        }]

        try:
            response = requests.post(api_url, json=job_data, headers=headers, timeout=10)
            response.raise_for_status()
        except Exception as e:
            raise UserError(f"Packsize job request failed: {e}")

        return f"Packsize job sent successfully (test_mode={test_mode}). Response: {response.text}"
