import os
import json
import uuid
import logging
import sqlite3

import fitz
import requests

from lxml import etree

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import parser_classes, api_view, permission_classes

log = logging.getLogger(__name__)

SIGNATURE_W = 0.2323
SIGNATURE_H = 0.0320

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def upload_pdf(request: Request):
    pdf = request.FILES["pdf"]
    log.info("upload pdf %s", pdf)

    content = pdf.read()
    filename = pdf.name
    folder_name = request.data.get("folder_name", "")
    name = request.data.get("name", filename)

    with requests.Session() as session:
        with session.get("https://esign.iotinga.it/sign_in") as response:
            xml = etree.HTML(response.text)
            authenticity_token = xml.xpath("//input[@name='authenticity_token'][1]")[0].get(
                "value"
            )
            if response.status_code != 200:
                raise RuntimeError("get sign in failed")

        with session.post(
            "https://esign.iotinga.it/sign_in",
            data={
                "authenticity_token": authenticity_token,
                "user[email]": os.environ["TARS_USERNAME"],
                "user[password]": os.environ["TARS_PASSWORD"],
            },
        ) as response:
            if response.status_code != 200:
                raise RuntimeError("sign in failed")

        with session.get("https://esign.iotinga.it") as response:
            if response.status_code != 200:
                raise RuntimeError("get / failed")

            xml = etree.HTML(response.text)
            authenticity_token = xml.xpath("//input[@name='authenticity_token'][1]")[0].get(
                "value"
            )
            form_id = xml.xpath("//input[@name='form_id'][1]")[0].get("value")
            csrf_token = xml.xpath("//meta[@name='csrf-token'][1]")[0].get("content")

        with session.post(
            "https://esign.iotinga.it/templates_upload",
            files={"files[]": (filename, content, "application/pdf")},
            data={
                "authenticity_token": authenticity_token,
                "form_id": form_id,
                "folder_name": folder_name,
            },
            headers={"X-CSRF-Token": csrf_token},
        ) as response:
            if response.status_code != 200:
                raise RuntimeError("put doc failed")

            xml = etree.HTML(response.text)
            result = json.loads(xml.xpath("//template-builder[1]")[0].get("data-template"))

    fields = []
    submitters = []
    pdf = fitz.open("pdf", content)
    for page_idx, page in enumerate(pdf.pages()):
        page_size: fitz.Point = page.mediabox_size
        for link in page.links():
            parts = link.get("nameddest", "").split("Submitter")
            if len(parts) == 2:
                submitter = parts[1]
                rect = link["from"]

                submitter_uuid = str(uuid.uuid4())
                fields.append({
                    "uuid": str(uuid.uuid4()),
                    "submitter_uuid": submitter_uuid,
                    "name": "",
                    "type": "signature",
                    "required": True,
                    "preferences": {},
                    "areas": [{
                        "x": rect.x0 / page_size.x,
                        "y": rect.y0 / page_size.y - SIGNATURE_H,
                        "h": SIGNATURE_H,
                        "w": SIGNATURE_W,
                        "attachment_uuid": result["schema"][0]["attachment_uuid"],
                        "page": page_idx
                    }],
                })
                submitters.append({
                    "name": f"Submitter{submitter}",
                    "uuid": submitter_uuid,
                })

    with sqlite3.connect(os.environ["TARS_DBPATH"]) as conn:
        conn.execute("""
            UPDATE templates 
            SET fields = ?, 
                submitters = ?, 
                name = ?,
                author_id = (SELECT id FROM users WHERE email = ?)
            WHERE id = ?
        """, [json.dumps(fields), json.dumps(submitters), name, request.user.email, result["id"]])
        conn.commit()

    result["submitters"] = submitters
    result["fields"] = fields
    result["name"] = name

    return Response(result)
