"""Answer Engine Optimization service helpers."""
from app.models import Page
from app.services.seo_service import SEOService


class AEOService:
    """Compute answer-readiness signals from CMS and tool pages."""

    @staticmethod
    def _normalize_keywords(raw_keywords):
        if not raw_keywords:
            return []
        if isinstance(raw_keywords, (int, float)):
            return []
        if isinstance(raw_keywords, list):
            return [str(keyword).strip() for keyword in raw_keywords if str(keyword).strip()]
        return [segment.strip() for segment in str(raw_keywords).split(',') if segment.strip()]

    @staticmethod
    def _generate_questions(title, keywords):
        lower_title = (title or 'this page').strip()
        keyword_seed = keywords[0] if keywords else lower_title
        return [
            f'What is {lower_title}?',
            f'How does {keyword_seed} work?',
            f'When should you use {keyword_seed}?'
        ]

    @classmethod
    def _page_record(cls, page, site_url):
        seo = page.seo_metadata
        widgets = page.widgets or []
        keywords = cls._normalize_keywords(seo.keywords if seo else [])
        schema_markup = seo.schema_markup if seo else {}
        has_schema = bool(schema_markup)
        has_faq_widget = any(widget.widget_type == 'faq' for widget in widgets)
        has_faq_schema = isinstance(schema_markup, dict) and schema_markup.get('@type') == 'FAQPage'
        has_faq = has_faq_widget or has_faq_schema
        is_indexable = bool(seo.indexable) if seo else page.status == 'published'

        readiness_score = 30
        readiness_score += 25 if is_indexable else 0
        readiness_score += 20 if has_schema else 0
        readiness_score += 15 if has_faq else 0
        readiness_score += 10 if keywords else 0

        questions = cls._generate_questions(page.title, keywords)

        return {
            'id': f'cms-{page.id}',
            'title': page.title,
            'url': f"{site_url.rstrip('/')}/{page.slug}",
            'source': 'cms',
            'status': 'answer-ready' if readiness_score >= 75 else 'needs-work',
            'readinessScore': readiness_score,
            'hasSchema': has_schema,
            'hasFaq': has_faq,
            'isIndexable': is_indexable,
            'keywords': keywords,
            'primaryQuestion': questions[0],
            'questionCount': len(questions),
            'recommendedAction': 'Expand FAQ and schema markup' if readiness_score < 75 else 'Monitor answer coverage',
        }

    @classmethod
    def get_dashboard_pages(cls, site_url):
        records = []

        cms_pages = (
            Page.query
            .filter(Page.status.in_(['draft', 'published']))
            .order_by(Page.updated_at.desc(), Page.created_at.desc())
            .all()
        )
        for page in cms_pages:
            records.append(cls._page_record(page, site_url))

        for tool_page in SEOService.get_tool_pages(site_url):
            keywords = cls._normalize_keywords(tool_page.get('keywords', 0))
            title = tool_page.get('title', 'Tool page')
            readiness_score = 55 + (15 if tool_page.get('status') == 'indexed' else 0)
            questions = cls._generate_questions(title, keywords)
            records.append({
                'id': tool_page['id'],
                'title': title,
                'url': tool_page['url'],
                'source': 'tool',
                'status': 'answer-ready' if readiness_score >= 70 else 'needs-work',
                'readinessScore': readiness_score,
                'hasSchema': False,
                'hasFaq': False,
                'isIndexable': tool_page.get('status') == 'indexed',
                'keywords': keywords,
                'primaryQuestion': questions[0],
                'questionCount': len(questions),
                'recommendedAction': 'Add FAQ schema and intent-based summaries',
            })

        return sorted(records, key=lambda record: (-record['readinessScore'], record['title'].lower()))

    @classmethod
    def get_dashboard_summary(cls, site_url):
        pages = cls.get_dashboard_pages(site_url)
        total_pages = len(pages)
        answer_ready = sum(1 for page in pages if page['status'] == 'answer-ready')
        schema_coverage = sum(1 for page in pages if page['hasSchema'])
        faq_coverage = sum(1 for page in pages if page['hasFaq'])
        avg_readiness = round(sum(page['readinessScore'] for page in pages) / total_pages, 1) if total_pages else 0

        return {
            'totalPages': total_pages,
            'answerReadyPages': answer_ready,
            'needsWorkPages': total_pages - answer_ready,
            'schemaCoverage': f"{round((schema_coverage / total_pages) * 100)}%" if total_pages else '0%',
            'faqCoverage': f"{round((faq_coverage / total_pages) * 100)}%" if total_pages else '0%',
            'averageReadiness': avg_readiness,
        }

    @classmethod
    def get_question_opportunities(cls, site_url):
        questions = []
        for page in cls.get_dashboard_pages(site_url):
            questions.append({
                'pageId': page['id'],
                'title': page['title'],
                'question': page['primaryQuestion'],
                'source': page['source'],
                'score': page['readinessScore'],
            })
        return questions[:12]