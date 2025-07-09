from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timezone
import json
import os
import time

class DriveService:
    def __init__(self, root_folder_name, metadata_file):
        """Initialize Google Drive API service with proper credentials"""
        self.root_folder_name = root_folder_name
        self.metadata_file = metadata_file
        
        # Configuration - Update path to your service account JSON
        SERVICE_ACCOUNT_FILE = "wide-planet-449115-b2-c6af973cadb6.json"
        SCOPES = ['https://www.googleapis.com/auth/drive']
        
        if not os.path.exists(SERVICE_ACCOUNT_FILE):
            raise FileNotFoundError(f"Service account file not found at: {SERVICE_ACCOUNT_FILE}")
        
        try:
            self.credentials = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE,
                scopes=SCOPES
            )
            
            self.service = build('drive', 'v3', 
                              credentials=self.credentials,
                              static_discovery=False)
            
            self.sa_email = self.credentials.service_account_email
            
            self.root_folder = self._get_root_folder()
            self.metadata = self._load_metadata()
            self._verify_permissions()
            
        except Exception as e:
            raise Exception(f"Drive API initialization failed: {str(e)}")

    def _get_root_folder(self):
        """Get or create the root folder"""
        query = f"name='{self.root_folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = self.service.files().list(
            q=query, 
            fields="files(id,name)",
            supportsAllDrives=True
        ).execute()
        
        if results.get('files'):
            return results['files'][0]
        
        folder_metadata = {
            'name': self.root_folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        return self.service.files().create(
            body=folder_metadata, 
            fields='id,name'
        ).execute()

    def _load_metadata(self):
        """Load the metadata file from Drive"""
        try:
            query = f"name='{self.metadata_file}' and mimeType='application/json' and '{self.root_folder['id']}' in parents and trashed=false"
            results = self.service.files().list(
                q=query, 
                fields="files(id)",
                supportsAllDrives=True
            ).execute()
            
            if not results.get('files'):
                raise FileNotFoundError("No metadata file found in Drive")
            
            file_id = results['files'][0]['id']
            request = self.service.files().get_media(fileId=file_id)
            metadata = json.loads(request.execute().decode('utf-8'))
            
            for date_str, folder_data in metadata['date_folders'].items():
                try:
                    folder = self.service.files().get(
                        fileId=folder_data['folder_id'],
                        fields='webViewLink,permissions',
                        supportsAllDrives=True
                    ).execute()
                    folder_data.update({
                        'folder_link': folder.get('webViewLink'),
                        'accessible': any(
                            perm.get('emailAddress') == self.sa_email
                            for perm in folder.get('permissions', [])
                        )
                    })
                except Exception as e:
                    print(f"Error processing folder {date_str}: {str(e)}")
                    folder_data['accessible'] = False
            
            return metadata
            
        except FileNotFoundError:
            return {
                'root_folder_id': self.root_folder['id'],
                'date_folders': {},
                'created_at': datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            raise Exception(f"Metadata loading failed: {str(e)}")

    def _verify_permissions(self):
        """Ensure service account has access to all folders"""
        try:
            for date_str, folder_data in self.metadata['date_folders'].items():
                if not folder_data.get('accessible', False):
                    self.service.permissions().create(
                        fileId=folder_data['folder_id'],
                        body={
                            'type': 'user',
                            'role': 'writer',
                            'emailAddress': self.sa_email
                        },
                        fields='id',
                        supportsAllDrives=True
                    ).execute()
                    time.sleep(0.5)
                    folder_data['accessible'] = True
                    
        except Exception as e:
            print(f"Permission verification warning: {str(e)}")

    def get_available_dates(self, force_refresh=False, current_date_only=False):
        """Get dates, optionally filtered to current date only"""
        if force_refresh or not hasattr(self, '_cached_dates'):
            self._cached_dates = self._load_fresh_dates()
        
        if current_date_only:
            today = datetime.now().strftime("%m/%d/%Y")
            return [d for d in self._cached_dates if d['display_date'] == today]
        
        return self._cached_dates

    def _load_fresh_dates(self):
        """Force a fresh load of dates from Drive"""
        dates = []
        self.metadata = self._load_metadata()
        
        for date_str, folder_data in self.metadata['date_folders'].items():
            try:
                query = f"'{folder_data['folder_id']}' in parents and trashed=false"
                results = self.service.files().list(
                    q=query,
                    fields="files(id,mimeType,name)",
                    supportsAllDrives=True
                ).execute()
                
                items = results.get('files', [])
                image_count = sum(1 for f in items if 'image' in f.get('mimeType', '').lower())
                video_count = sum(1 for f in items if 'video' in f.get('mimeType', '').lower())
                
                # Count mask and gloves violations
                mask_count = sum(1 for f in items if 'no-mask' in f.get('name', '').lower())
                gloves_count = sum(1 for f in items if 'no-gloves' in f.get('name', '').lower())
                
                dates.append({
                    'display_date': folder_data['display_date'],
                    'folder_link': folder_data.get('folder_link', ''),
                    'folder_id': folder_data['folder_id'],
                    'violations_count': image_count,
                    'images_uploaded': image_count,
                    'videos_count': video_count,
                    'mask_count': mask_count,
                    'gloves_count': gloves_count,
                    'accessible': True,
                    'actual_files_count': len(items)
                })
                
            except Exception as e:
                print(f"Error processing folder {date_str}: {str(e)}")
                continue
        
        return sorted(
            dates,
            key=lambda x: datetime.strptime(x['display_date'], "%m/%d/%Y"),
            reverse=True
        )

    def share_folder(self, email):
        """Share the root folder with specified email"""
        try:
            permission = {
                'type': 'user',
                'role': 'writer',
                'emailAddress': email
            }
            self.service.permissions().create(
                fileId=self.root_folder['id'],
                body=permission,
                fields='id',
                supportsAllDrives=True,
                sendNotificationEmail=True
            ).execute()
            return True
        except Exception as e:
            print(f"Error sharing folder: {str(e)}")
            return False