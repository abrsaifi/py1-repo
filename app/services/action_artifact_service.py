"""Concrete SEO and AEO action workflows with artifact generation."""
from collections import defaultdict
from datetime import datetime, timezone
import json
import os

from flask import current_app

from app.services.aeo_service import AEOService
from app.services.seo_service import SEOService


class ActionArtifactService:
    """Persist generated SEO and AEO action artifacts to disk."""

    @staticmethod
    def _artifact_dir(section):
        base_dir = os.path.join(current_app.instance_path, 'action-artifacts', section)
        os.makedirs(base_dir, exist_ok=True)
        return base_dir

    @staticmethod
    def _write_json(section, prefix, payload):
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
        filename = f'{prefix}-{timestamp}.json'
        path = os.path.join(ActionArtifactService._artifact_dir(section), filename)
        with open(path, 'w', encoding='utf-8') as handle:
            json.dump(payload, handle, indent=2)
        return filename

    @staticmethod
    def _write_text(section, prefix, content, extension):
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
        filename = f'{prefix}-{timestamp}.{extension}'
        path = os.path.join(ActionArtifactService._artifact_dir(section), filename)
        with open(path, 'w', encoding='utf-8') as handle:
            handle.write(content)
        return filename

    @staticmethod
    def refresh_seo(site_url):
        summary = SEOService.get_dashboard_summary(site_url)
        pages = SEOService.get_dashboard_pages(site_url)
        sitemap_xml = SEOService.build_sitemap_xml(site_url)
        generated_at = datetime.now(timezone.utc).isoformat()

        report_filename = ActionArtifactService._write_json('seo', 'summary', {
            'generated_at': generated_at,
            'summary': summary,
            'pages': pages,
        })
        sitemap_filename = ActionArtifactService._write_text('seo', 'sitemap', sitemap_xml, 'xml')

        return {
            'message': 'SEO summary regenerated from live page inventory',
            'generated_at': generated_at,
            'summary': summary,
            'artifacts': {
                'report': report_filename,
                'sitemap': sitemap_filename,
            },
        }

    @staticmethod
    def submit_sitemap(site_url):
        summary = SEOService.get_dashboard_summary(site_url)
        payload = {
            'requested_at': datetime.now(timezone.utc).isoformat(),
            'sitemap_url': f'{site_url.rstrip("/")}/sitemap.xml',
            'page_count': summary.get('totalPages', 0),
            'indexed_pages': summary.get('indexedPages', 0),
            'status': 'prepared',
        }
        artifact = ActionArtifactService._write_json('seo', 'submit-sitemap', payload)
        return {
            'message': 'Sitemap submission package prepared',
            'submission': payload,
            'artifact': artifact,
        }

    @staticmethod
    def queue_reindex(site_url):
        pages = SEOService.get_dashboard_pages(site_url)
        candidates = [
            {
                'id': page.get('id'),
                'title': page.get('title'),
                'status': page.get('status'),
            }
            for page in pages
            if page.get('status') != 'indexed'
        ]
        payload = {
            'requested_at': datetime.now(timezone.utc).isoformat(),
            'candidate_count': len(candidates),
            'candidates': candidates,
        }
        artifact = ActionArtifactService._write_json('seo', 'reindex', payload)
        return {
            'message': 'Reindex batch prepared from non-indexed pages',
            'reindex': payload,
            'artifact': artifact,
        }

    @staticmethod
    def refresh_aeo(site_url):
        summary = AEOService.get_dashboard_summary(site_url)
        pages = AEOService.get_dashboard_pages(site_url)
        questions = AEOService.get_question_opportunities(site_url)
        recommendations = [
            {
                'pageId': page.get('id'),
                'title': page.get('title'),
                'recommendedAction': page.get('recommendedAction'),
                'readinessScore': page.get('readinessScore'),
            }
            for page in pages[:10]
        ]
        payload = {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'summary': summary,
            'questions': questions,
            'recommendations': recommendations,
        }
        artifact = ActionArtifactService._write_json('aeo', 'recommendations', payload)
        return {
            'message': 'AEO recommendations rebuilt from current content and tool pages',
            'summary': summary,
            'artifact': artifact,
            'recommendations': recommendations,
        }

    @staticmethod
    def expand_faqs(site_url):
        questions = AEOService.get_question_opportunities(site_url)
        grouped = defaultdict(list)
        for item in questions:
            grouped[item.get('pageId')].append(item)

        suggestions = []
        for page_id, items in grouped.items():
            ordered = sorted(items, key=lambda item: item.get('score', 0), reverse=True)
            suggestions.append({
                'pageId': page_id,
                'title': ordered[0].get('title'),
                'suggestedFaqs': [entry.get('question') for entry in ordered[:3]],
            })

        payload = {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'page_count': len(suggestions),
            'suggestions': suggestions,
        }
        artifact = ActionArtifactService._write_json('aeo', 'faq-expansion', payload)
        return {
            'message': 'FAQ expansion suggestions generated from live question opportunities',
            'artifact': artifact,
            'faqSuggestions': suggestions,
        }