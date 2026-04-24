import logging
import uuid
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import File, UploadFile
from pydantic import BaseModel

from backend.db.dal import AssetsCreate, PhotobooksCreate
from backend.lib.job_manager.base import JobType
from backend.lib.types.asset import Asset
from backend.lib.utils.common import none_throws
from backend.lib.utils.web_requests import UploadFileTempDirManager
from backend.route_handler.base import RouteHandler


class UploadedFileInfo(BaseModel):
    filename: str
    storage_key: str


class FailedUploadInfo(BaseModel):
    filename: str
    error: str


class NewPhotobookResponse(BaseModel):
    job_id: UUID
    uploaded_files: list[UploadedFileInfo]
    failed_uploads: list[FailedUploadInfo]
    skipped_non_media: list[str]


class TimelensAPIHandler(RouteHandler):
    def register_routes(self) -> None:
        self.router.add_api_route(
            "/api/new_photobook",
            self.new_photobook,
            methods=["POST"],
            response_model=NewPhotobookResponse,
        )

    @staticmethod
    def is_accepted_mime(mime: Optional[str]) -> bool:
        return mime is not None and (
            mime.startswith("image/")
            # or mime.startswith("video/") # only images allowed for now
        )

    async def new_photobook(
        self,
        files: list[UploadFile] = File(...),
    ) -> NewPhotobookResponse:
        async with self.app.db_session_factory.session() as db_session:
            # Filter valid files according to FastAPI reported mime type
            valid_files = [
                file
                for file in files
                if TimelensAPIHandler.is_accepted_mime(file.content_type)
            ]
            file_names = [file.filename for file in valid_files]
            skipped = [
                file.filename
                for file in files
                if file not in valid_files and file.filename is not None
            ]
            logging.info({"accepted_files": file_names, "skipped_non_media": skipped})

            succeeded_uploads: list[UploadedFileInfo] = []
            failed_uploads: list[FailedUploadInfo] = []

            USER_ID_FIXME = uuid.uuid4()

            async with UploadFileTempDirManager(
                str(uuid.uuid4()),
                valid_files,  # FIXME
            ) as user_requested_uploads:
                # 1. Create photobook in DB
                photobook = await self.app.photobook_dal.create(
                    db_session,
                    PhotobooksCreate(
                        user_id=USER_ID_FIXME,  # FIXME: hardcoded
                        title=f"New Photobook {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                        caption=None,
                        theme=None,
                        status="pending",
                        user_provided_occasion=None,  # FIXME
                        user_provided_occasion_custom_details=None,
                    ),
                )
                await db_session.commit()

                upload_inputs = [
                    (
                        none_throws(asset.cached_local_path),
                        self.app.asset_manager.mint_asset_key(
                            photobook.id, none_throws(asset.cached_local_path).name
                        ),
                    )
                    for (_original_fname, asset) in user_requested_uploads
                ]
                upload_results = await self.app.asset_manager.upload_files_batched(
                    upload_inputs
                )
                asset_objs_to_create: list[AssetsCreate] = []

                # 2. Transform upload results into endpoint response
                for _original_fname, asset in user_requested_uploads:
                    upload_res = upload_results.get(
                        none_throws(asset.cached_local_path), None
                    )
                    if upload_res is None or isinstance(upload_res, Exception):
                        failed_uploads.append(
                            FailedUploadInfo(
                                filename=_original_fname, error=str(upload_res)
                            )
                        )
                    else:
                        assert isinstance(upload_res, Asset)
                        succeeded_uploads.append(
                            UploadedFileInfo(
                                filename=_original_fname,
                                storage_key=none_throws(upload_res.asset_storage_key),
                            )
                        )
                        asset_objs_to_create.append(
                            AssetsCreate(
                                user_id=USER_ID_FIXME,
                                asset_key_original=none_throws(
                                    upload_res.asset_storage_key
                                ),
                                asset_key_display=None,
                                asset_key_llm=None,
                                metadata_json={},
                                original_photobook_id=photobook.id,
                            )
                        )

            # ✅ Batch-insert assets
            created_assets = await self.app.assets_dal.create_many(
                db_session, asset_objs_to_create
            )
            await db_session.commit()

            # 3. Enqueue photobook generation job
            job_id = await self.app.job_manager.enqueue(
                db_session,
                JobType.PHOTOBOOK_GENERATION,
                USER_ID_FIXME,
                photobook,
                {
                    "asset_uuids": [str(asset.id) for asset in created_assets],
                },
            )

            return NewPhotobookResponse(
                job_id=job_id,
                uploaded_files=succeeded_uploads,
                failed_uploads=failed_uploads,
                skipped_non_media=skipped,
            )
