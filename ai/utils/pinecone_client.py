"""
Navelle AI Module — Pinecone Vector Store Client
Seeds and searches 23 perimenopause medical knowledge documents.
"""
from __future__ import annotations

import logging
from typing import Any

from ai.config import settings

logger = logging.getLogger(__name__)

# ── Medical knowledge base (23 perimenopause documents) ───────────────────────
MEDICAL_DOCUMENTS: list[dict] = [
    {
        "id": "doc_001",
        "topic": "Hot Flashes — Causes & Mechanisms",
        "content": (
            "Hot flashes (vasomotor symptoms) in perimenopause are caused by declining estrogen levels "
            "that disrupt the hypothalamic thermoregulatory system. The hypothalamus becomes hypersensitive "
            "to small temperature changes, triggering vasodilation and sweating. They typically last 1–5 minutes "
            "and can occur several times per day or night."
        ),
        "category": "symptoms",
        "keywords": ["hot flashes", "vasomotor", "estrogen", "hypothalamus", "thermoregulation"],
    },
    {
        "id": "doc_002",
        "topic": "Hot Flashes — Non-Hormonal Management",
        "content": (
            "Non-hormonal strategies to reduce hot flash frequency: (1) Avoid triggers: caffeine, alcohol, "
            "spicy foods, hot drinks, stress. (2) Dress in breathable layers you can remove quickly. "
            "(3) Keep the bedroom 18–20°C. (4) Cool wrists under cold water during a flash. "
            "(5) Cognitive-behavioural therapy (CBT) has Level A evidence for reducing hot flash distress. "
            "(6) Mind-body practices: paced breathing, mindfulness."
        ),
        "category": "management",
        "keywords": ["hot flashes", "non-hormonal", "CBT", "cooling", "triggers", "breathing"],
    },
    {
        "id": "doc_003",
        "topic": "Hot Flashes — Hormonal Treatment (HRT)",
        "content": (
            "Hormone Replacement Therapy (HRT) is the most effective treatment for vasomotor symptoms. "
            "Systemic estrogen reduces hot flash frequency by 75–90%. Types include: transdermal patches, "
            "gels, sprays, oral tablets. For women with a uterus, progesterone must be added to protect "
            "the uterine lining. Benefits: sleep improvement, mood stabilisation, bone protection. "
            "Individual risk/benefit assessment with a doctor is essential."
        ),
        "category": "treatment",
        "keywords": ["HRT", "hormone replacement", "estrogen", "progesterone", "hot flashes", "menopause treatment"],
    },
    {
        "id": "doc_004",
        "topic": "Night Sweats — Understanding & Differentiation",
        "content": (
            "Night sweats in perimenopause are nocturnal hot flashes triggered by hormonal fluctuations. "
            "They differ from simple overheating: they can drench bedclothes and interrupt sleep multiple times. "
            "Night sweats disrupt sleep architecture, reducing slow-wave and REM sleep. "
            "They are distinct from secondary causes (infection, medications, thyroid disorders) — "
            "a healthcare provider should rule out other causes if symptoms are severe."
        ),
        "category": "symptoms",
        "keywords": ["night sweats", "nocturnal", "sleep disruption", "perimenopause", "hormones"],
    },
    {
        "id": "doc_005",
        "topic": "Night Sweats — Sleep Hygiene Strategies",
        "content": (
            "Evidence-based sleep strategies for night sweats: (1) Cooling mattress pad or bamboo sheets "
            "(moisture-wicking). (2) Bedroom temperature 18–20°C. (3) Avoid alcohol within 3 hours of bed — "
            "it worsens night sweats. (4) Shower with cool water before bed lowers core temperature. "
            "(5) Keep ice water on the bedside table. (6) Consistent sleep/wake schedule stabilises "
            "circadian rhythm. (7) CBT for Insomnia (CBT-I) has strong Level A evidence."
        ),
        "category": "management",
        "keywords": ["night sweats", "sleep hygiene", "cooling", "CBT-I", "insomnia", "alcohol"],
    },
    {
        "id": "doc_006",
        "topic": "Mood Swings — Estrogen & Serotonin Connection",
        "content": (
            "Estrogen modulates serotonin, dopamine, and norepinephrine pathways in the brain. "
            "During perimenopause, fluctuating estrogen causes instability in these neurotransmitter systems, "
            "producing mood swings, irritability, and emotional sensitivity. "
            "This is distinct from clinical depression but can predispose to it. "
            "Women with a history of PMS or postnatal depression have higher susceptibility."
        ),
        "category": "symptoms",
        "keywords": ["mood swings", "estrogen", "serotonin", "dopamine", "neurotransmitters", "irritability"],
    },
    {
        "id": "doc_007",
        "topic": "Mood Changes — Anxiety During Perimenopause",
        "content": (
            "Anxiety is one of the most common but underrecognised symptoms of perimenopause. "
            "It can manifest as generalised anxiety, panic attacks, or heightened worry. "
            "The hypothalamic-pituitary-adrenal (HPA) axis dysregulation contributes. "
            "Evidence-based approaches: aerobic exercise (150 min/week), mindfulness-based stress "
            "reduction (MBSR), and CBT. SSRIs and SNRIs are effective pharmacological options. "
            "HRT can also reduce anxiety by stabilising estrogen levels."
        ),
        "category": "mental_health",
        "keywords": ["anxiety", "perimenopause", "panic attacks", "MBSR", "CBT", "HRT", "SSRI"],
    },
    {
        "id": "doc_008",
        "topic": "Mood Changes — Depression Risk & Support",
        "content": (
            "The menopausal transition is a window of vulnerability for depression. "
            "Risk doubles during perimenopause versus premenopause. "
            "Key risk factors: previous depressive episodes, sleep disruption, stressful life events. "
            "First-line treatments: antidepressants (SSRIs, SNRIs), psychotherapy (CBT), exercise. "
            "HRT may reduce depressive symptoms in perimenopausal women. "
            "Always seek professional evaluation — do not self-diagnose or self-treat depression."
        ),
        "category": "mental_health",
        "keywords": ["depression", "perimenopause", "antidepressants", "CBT", "HRT", "mental health"],
    },
    {
        "id": "doc_009",
        "topic": "Brain Fog — Cognitive Changes in Perimenopause",
        "content": (
            "Brain fog encompasses: difficulty concentrating, word-finding problems, memory lapses, "
            "slowed processing speed. It peaks during the menopausal transition and improves "
            "post-menopause for most women. Caused by: estrogen withdrawal, sleep disruption, "
            "stress, and anxiety. SWAN study data confirm this is a real, measurable phenomenon, "
            "not just perceived. Women often describe it as 'losing their sharpness'."
        ),
        "category": "symptoms",
        "keywords": ["brain fog", "cognitive", "memory", "concentration", "estrogen", "SWAN study"],
    },
    {
        "id": "doc_010",
        "topic": "Brain Fog — Management Strategies & Nutrition",
        "content": (
            "Evidence-based strategies for brain fog: (1) Aerobic exercise — 30 min, 5x/week — "
            "increases BDNF (brain-derived neurotrophic factor) and improves memory. "
            "(2) Omega-3 fatty acids (EPA/DHA): 1–2g/day, found in oily fish or supplements. "
            "(3) Mediterranean diet rich in leafy greens, berries, and olive oil supports brain health. "
            "(4) Adequate sleep is critical — even one night of poor sleep impairs working memory. "
            "(5) Cognitive strategies: lists, calendars, 'name it to tame it'."
        ),
        "category": "management",
        "keywords": ["brain fog", "omega-3", "exercise", "BDNF", "Mediterranean diet", "sleep", "cognitive strategies"],
    },
    {
        "id": "doc_011",
        "topic": "Sleep — Hormonal Impact on Sleep Architecture",
        "content": (
            "Estrogen and progesterone both influence sleep. Progesterone has sedative properties "
            "(promotes GABA-A receptor activity). As both decline, sleep architecture shifts: "
            "less slow-wave (deep) sleep, more awakenings, reduced REM sleep. "
            "Insomnia affects 40–60% of perimenopausal women. Night sweats are a major disruptor. "
            "Poor sleep amplifies all other perimenopausal symptoms — mood, cognition, pain sensitivity."
        ),
        "category": "symptoms",
        "keywords": ["sleep", "progesterone", "estrogen", "insomnia", "REM", "slow-wave sleep", "GABA"],
    },
    {
        "id": "doc_012",
        "topic": "Sleep — CBT-I for Menopausal Insomnia",
        "content": (
            "Cognitive Behavioural Therapy for Insomnia (CBT-I) is the first-line treatment for "
            "chronic insomnia, including menopausal insomnia. Components: (1) Sleep restriction therapy, "
            "(2) Stimulus control, (3) Sleep hygiene education, (4) Cognitive restructuring (challenging "
            "anxiety about sleep). CBT-I is superior to sleeping pills long-term and has no side effects. "
            "Digital CBT-I programmes (Sleepio, etc.) are equally effective. Takes 6–8 weeks of practice."
        ),
        "category": "treatment",
        "keywords": ["CBT-I", "insomnia", "sleep therapy", "cognitive behavioural", "sleep restriction", "stimulus control"],
    },
    {
        "id": "doc_013",
        "topic": "Weight & Metabolism — Changes During Perimenopause",
        "content": (
            "Women gain an average of 1.5 kg per year during the menopausal transition, independent of diet. "
            "Causes: declining estrogen shifts fat distribution from hips/thighs to abdomen (visceral fat). "
            "Metabolic rate decreases. Insulin sensitivity declines. Muscle mass reduces (sarcopenia). "
            "Visceral fat is a risk factor for cardiovascular disease and type 2 diabetes. "
            "Weight management requires a combined approach of diet, strength training, and cardio."
        ),
        "category": "symptoms",
        "keywords": ["weight gain", "metabolism", "estrogen", "visceral fat", "sarcopenia", "insulin resistance", "abdomen"],
    },
    {
        "id": "doc_014",
        "topic": "Weight — Exercise & Dietary Strategies",
        "content": (
            "Recommended strategies: (1) Resistance/strength training 2–3x/week — builds muscle, "
            "raises metabolic rate. (2) 150 min moderate aerobic exercise per week. "
            "(3) Protein intake: 1.2–1.6g/kg body weight preserves muscle. "
            "(4) Mediterranean or DASH diet reduces visceral fat. "
            "(5) Limit processed foods and refined carbohydrates. "
            "(6) Intermittent fasting may help but consult a doctor first. "
            "(7) Alcohol significantly worsens weight gain in this period."
        ),
        "category": "management",
        "keywords": ["weight", "exercise", "protein", "strength training", "Mediterranean diet", "alcohol"],
    },
    {
        "id": "doc_015",
        "topic": "Sexual Health — Vaginal Dryness & Libido",
        "content": (
            "Genitourinary Syndrome of Menopause (GSM) affects 50–80% of postmenopausal women. "
            "Symptoms: vaginal dryness, irritation, dyspareunia (painful sex), urinary urgency. "
            "Cause: estrogen-dependent tissue atrophy. Treatments: (1) Vaginal estrogen (low-dose, safe "
            "even for most breast cancer survivors), (2) Non-hormonal lubricants/moisturisers, "
            "(3) Ospemifene (oral SERM). Libido changes are multifactorial: hormonal, psychological, "
            "relationship, and medication-related. Open conversation with your doctor is essential."
        ),
        "category": "sexual_health",
        "keywords": ["vaginal dryness", "libido", "GSM", "sexual health", "estrogen", "lubricants", "dyspareunia"],
    },
    {
        "id": "doc_016",
        "topic": "Menstrual Changes — Irregular Cycles Explained",
        "content": (
            "Irregular periods are the hallmark of perimenopause. Changes include: shorter or longer cycles, "
            "heavier or lighter flow, skipped periods. The ovaries produce less estrogen and progesterone "
            "inconsistently. Anovulatory cycles (no ovulation) become more common. "
            "Note: pregnancy is still possible during perimenopause — contraception is advised "
            "until 12 months after the last period (menopause). Track cycles with an app or journal. "
            "Seek advice if bleeding is very heavy or occurs between periods."
        ),
        "category": "menstrual",
        "keywords": ["irregular periods", "menstrual cycle", "perimenopause", "anovulatory", "contraception", "heavy bleeding"],
    },
    {
        "id": "doc_017",
        "topic": "Hormone Testing — FSH, Estradiol & What to Ask",
        "content": (
            "Key hormone tests: (1) FSH (Follicle Stimulating Hormone): elevated >30 IU/L suggests "
            "ovarian insufficiency, but FSH fluctuates in perimenopause and a single normal result "
            "doesn't rule it out. (2) Estradiol (E2): falling levels. (3) AMH: low indicates reduced "
            "ovarian reserve. In perimenopause, diagnosis is typically clinical (based on symptoms + age) "
            "rather than relying solely on blood tests. Ask your doctor: 'What do my results mean for "
            "my specific situation?' and 'Do I need repeat tests?'"
        ),
        "category": "testing",
        "keywords": ["FSH", "estradiol", "hormone test", "AMH", "ovarian reserve", "blood test", "perimenopause diagnosis"],
    },
    {
        "id": "doc_018",
        "topic": "HRT — Types, Benefits & Risks Overview",
        "content": (
            "HRT types: (1) Combined HRT (estrogen + progesterone) — for women with a uterus. "
            "(2) Estrogen-only — for women without a uterus. (3) Testosterone — for libido in some women. "
            "Benefits: reduces hot flashes by 75–90%, improves sleep, mood, cognitive function, "
            "bone density, and reduces cardiovascular risk when started before 60. "
            "Risks: small increased risk of breast cancer with combined HRT after 5+ years, "
            "DVT risk (lower with transdermal). The 2002 WHI study overestimated risks; "
            "current guidelines support HRT for most healthy perimenopausal women. "
            "Individual assessment with a menopause specialist is recommended."
        ),
        "category": "treatment",
        "keywords": ["HRT", "hormone replacement", "estrogen", "progesterone", "testosterone", "breast cancer risk", "WHI"],
    },
    {
        "id": "doc_019",
        "topic": "Perimenopause vs Menopause — What's the Difference",
        "content": (
            "Perimenopause: the transition period before menopause, lasting 4–10 years. "
            "Characterised by irregular periods and fluctuating hormone levels. Can start in early 40s. "
            "Menopause: defined as 12 consecutive months without a menstrual period. "
            "Average age: 51 in the UK/USA. Postmenopause: the rest of life after menopause. "
            "Symptoms often peak in perimenopause and improve post-menopause, though some (GSM) "
            "worsen without treatment. Premature menopause (POI) is before age 40 — requires specialist care."
        ),
        "category": "education",
        "keywords": ["perimenopause", "menopause", "postmenopause", "POI", "premature menopause", "definition", "stages"],
    },
    {
        "id": "doc_020",
        "topic": "Perimenopause Timeline — What to Expect",
        "content": (
            "Typical perimenopause progression: Early stage (3–5 years before menopause): "
            "cycles become irregular, PMS worsens, sleep changes. Late stage (1–3 years): "
            "cycles very irregular (>60 days apart), hot flashes intensify, vaginal changes begin. "
            "Menopause: 12 months no period. Postmenopause: vasomotor symptoms improve for most "
            "but vaginal symptoms may persist/worsen. Bone density declines accelerate in the "
            "first 5 years post-menopause. Cardiovascular risk increases post-menopause."
        ),
        "category": "education",
        "keywords": ["perimenopause timeline", "stages", "early perimenopause", "late perimenopause", "bone density", "cardiovascular"],
    },
    {
        "id": "doc_021",
        "topic": "Joint Pain & Musculoskeletal Symptoms",
        "content": (
            "Oestrogen has anti-inflammatory properties; its decline leads to increased joint pain "
            "and stiffness (arthralgia) in 50–60% of perimenopausal women. Commonly affects knees, "
            "hands, and hips. Strategies: (1) Low-impact exercise: swimming, cycling, yoga. "
            "(2) Anti-inflammatory diet: omega-3, turmeric, cherries, berries. "
            "(3) Strength training protects joints by building supporting muscle. "
            "(4) HRT can reduce arthralgia in some women. "
            "(5) Always rule out rheumatoid arthritis and osteoarthritis with your doctor."
        ),
        "category": "symptoms",
        "keywords": ["joint pain", "arthralgia", "estrogen", "inflammation", "yoga", "exercise", "anti-inflammatory"],
    },
    {
        "id": "doc_022",
        "topic": "Bone Health — Osteoporosis Risk & Prevention",
        "content": (
            "Estrogen is essential for maintaining bone density. In the 5 years following menopause, "
            "women lose 10–20% of bone density, significantly raising osteoporosis risk. "
            "Risk factors: smoking, low BMI, family history, low calcium intake, sedentary lifestyle. "
            "Prevention: (1) Calcium 1000–1200 mg/day from food (dairy, leafy greens). "
            "(2) Vitamin D 800–1000 IU/day. (3) Weight-bearing exercise (walking, dancing). "
            "(4) HRT is the most effective prevention for postmenopausal bone loss. "
            "(5) DEXA scan recommended at menopause for high-risk individuals."
        ),
        "category": "bone_health",
        "keywords": ["osteoporosis", "bone density", "estrogen", "calcium", "vitamin D", "DEXA", "fracture risk"],
    },
    {
        "id": "doc_023",
        "topic": "Fatigue — Causes & Evidence-Based Management",
        "content": (
            "Perimenopausal fatigue is multifactorial: sleep disruption (night sweats), anaemia, "
            "thyroid dysfunction, depression, and direct hormonal effects on energy metabolism. "
            "Investigation: CBC (anaemia), thyroid function tests, ferritin, vitamin D, B12. "
            "Management: (1) Treat underlying causes (iron, thyroid, etc.). "
            "(2) Aerobic exercise paradoxically reduces fatigue — start with 10-minute walks. "
            "(3) Pacing techniques — activity management. "
            "(4) HRT improves energy levels in many women. "
            "(5) Avoid caffeine after 2pm to protect sleep quality."
        ),
        "category": "symptoms",
        "keywords": ["fatigue", "energy", "anaemia", "thyroid", "exercise", "iron", "vitamin D", "sleep"],
    },
]


class PineconeClient:
    """
    Wrapper around Pinecone for perimenopause medical knowledge.
    Initialises lazily to avoid blocking app startup.
    """

    def __init__(self) -> None:
        self._index = None
        self._embeddings = None
        self._ready = False

    def _init(self) -> bool:
        """
        Lazy initialisation. Returns True if ready, False if credentials are missing.
        """
        if self._ready:
            return True

        if not settings.pinecone_api_key or not settings.openai_api_key:
            logger.warning(
                "Pinecone or OpenAI credentials not configured — vector search unavailable."
            )
            return False

        try:
            from pinecone import Pinecone, ServerlessSpec  # type: ignore
            from langchain_openai import OpenAIEmbeddings

            pc = Pinecone(api_key=settings.pinecone_api_key)
            index_name = settings.pinecone_index_name

            # Create index if it doesn't exist
            existing = [idx.name for idx in pc.list_indexes()]
            if index_name not in existing:
                logger.info("Creating Pinecone index: %s", index_name)
                pc.create_index(
                    name=index_name,
                    dimension=1536,  # text-embedding-ada-002 dimension
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region=settings.pinecone_environment),
                )

            self._index = pc.Index(index_name)
            self._embeddings = OpenAIEmbeddings(
                api_key=settings.openai_api_key,
                model="text-embedding-ada-002",
            )
            self._ready = True
            logger.info("Pinecone client initialised — index: %s", index_name)
            return True

        except Exception as exc:
            logger.error("Pinecone initialisation failed: %s", exc)
            return False

    async def seed_documents(self, force: bool = False) -> int:
        """
        Embed and upsert all medical documents into Pinecone.
        Skips if already seeded (unless force=True).
        Returns count of documents upserted.
        """
        if not self._init():
            return 0

        try:
            # Check if already seeded
            stats = self._index.describe_index_stats()
            if stats.get("total_vector_count", 0) >= len(MEDICAL_DOCUMENTS) and not force:
                logger.info("Pinecone already seeded (%d vectors) — skipping", stats["total_vector_count"])
                return 0

            logger.info("Seeding %d medical documents into Pinecone...", len(MEDICAL_DOCUMENTS))
            texts = [doc["content"] for doc in MEDICAL_DOCUMENTS]
            embeddings = self._embeddings.embed_documents(texts)

            vectors = [
                (
                    doc["id"],
                    embedding,
                    {
                        "topic": doc["topic"],
                        "category": doc["category"],
                        "content": doc["content"][:1000],  # store first 1000 chars as metadata
                        "keywords": ", ".join(doc.get("keywords", [])),
                    },
                )
                for doc, embedding in zip(MEDICAL_DOCUMENTS, embeddings)
            ]

            # Upsert in batches of 10
            batch_size = 10
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i : i + batch_size]
                self._index.upsert(vectors=batch)

            logger.info("Successfully seeded %d documents", len(MEDICAL_DOCUMENTS))
            return len(MEDICAL_DOCUMENTS)

        except Exception as exc:
            logger.error("Failed to seed Pinecone: %s", exc)
            return 0

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Search for the most relevant medical documents for a query.
        Returns list of { topic, content, category, score }.
        """
        if not self._init():
            logger.warning("Pinecone not available — returning empty results")
            return []

        try:
            query_embedding = self._embeddings.embed_query(query)
            results = self._index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
            )
            return [
                {
                    "topic": match.get("metadata", {}).get("topic", ""),
                    "content": match.get("metadata", {}).get("content", ""),
                    "category": match.get("metadata", {}).get("category", ""),
                    "score": round(match.get("score", 0), 3),
                }
                for match in results.get("matches", [])
                if match.get("score", 0) > 0.6  # relevance threshold
            ]
        except Exception as exc:
            logger.error("Pinecone search failed: %s", exc)
            return []

    def store_user_documents(
        self,
        user_id: str,
        document_chunks: list[dict],
    ) -> int:
        """
        Store user document chunks in Pinecone for personalized RAG.

        Args:
            user_id: User identifier
            document_chunks: Processed document chunks from document_processor

        Returns:
            Number of chunks stored
        """
        if not self._init():
            logger.warning("Pinecone not available — cannot store user documents")
            return 0

        if not document_chunks:
            return 0

        try:
            logger.info(
                "Storing %d document chunks for user %s", len(document_chunks), user_id
            )

            # Prepare texts for embedding
            texts = [chunk["content"] for chunk in document_chunks]
            embeddings = self._embeddings.embed_documents(texts)

            # Prepare vectors with metadata
            vectors = []
            for chunk, embedding in zip(document_chunks, embeddings):
                vector_id = f"user_{user_id}_{chunk['id']}"
                metadata = {
                    "user_id": user_id,
                    "document_id": chunk["document_id"],
                    "document_title": chunk["document_title"],
                    "document_type": chunk["document_type"],
                    "category": chunk.get("category", "General"),
                    "chunk_index": chunk["chunk_index"],
                    "total_chunks": chunk["total_chunks"],
                    "content_preview": chunk["content"][:500],  # First 500 chars
                    "is_user_document": True,  # Flag to identify user docs vs general knowledge
                    **chunk.get("metadata", {}),
                }
                vectors.append((vector_id, embedding, metadata))

            # Upsert in batches of 10
            batch_size = 10
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i : i + batch_size]
                self._index.upsert(vectors=batch)

            logger.info(
                "Successfully stored %d user document chunks for user %s",
                len(vectors),
                user_id,
            )
            return len(vectors)

        except Exception as exc:
            logger.error("Failed to store user documents: %s", exc)
            return 0

    def search_user_documents(
        self,
        user_id: str,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:
        """
        Search within a specific user's documents.

        Args:
            user_id: User identifier
            query: Search query
            top_k: Number of results

        Returns:
            List of matching document chunks
        """
        if not self._init():
            return []

        try:
            query_embedding = self._embeddings.embed_query(query)

            # Search with filter for user_id
            results = self._index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter={"user_id": user_id, "is_user_document": True},
            )

            return [
                {
                    "document_title": match.get("metadata", {}).get("document_title", ""),
                    "document_type": match.get("metadata", {}).get("document_type", ""),
                    "category": match.get("metadata", {}).get("category", ""),
                    "content_preview": match.get("metadata", {}).get("content_preview", ""),
                    "chunk_index": match.get("metadata", {}).get("chunk_index", 0),
                    "score": round(match.get("score", 0), 3),
                }
                for match in results.get("matches", [])
                if match.get("score", 0) > 0.6
            ]

        except Exception as exc:
            logger.error("User document search failed: %s", exc)
            return []


# ── Singleton ──────────────────────────────────────────────────────────────────
pinecone_client = PineconeClient()
