# ─────────────────────────────────────────────────────────────────────────────
# config.py  –  VBCUA App-wide configuration
# ─────────────────────────────────────────────────────────────────────────────

APP_TITLE = "VBCUA – Voice-Based Concept Understanding Analyser"
APP_ICON  = "🎙️"
APP_VERSION = "1.0.0"

# ── Whisper model size ────────────────────────────────────────────────────────
WHISPER_MODEL = "base"   # options: tiny | base | small | medium | large

# ── Sentence-BERT model ───────────────────────────────────────────────────────
SBERT_MODEL = "all-MiniLM-L6-v2"

# ── Scoring weights (must sum to 1.0) ─────────────────────────────────────────
WEIGHT_SEMANTIC = 0.60
WEIGHT_FLUENCY  = 0.40

# ── Comprehension label thresholds (based on weighted final score) ─────────────
SCORE_STRONG   = 0.75
SCORE_MODERATE = 0.50
# below SCORE_MODERATE → "Poor Understanding"

# ── Filler words to detect ────────────────────────────────────────────────────
FILLER_WORDS = [
    "um", "uh", "umm", "uhh", "er", "err",
    "like", "you know", "basically", "actually",
    "literally", "sort of", "kind of", "right",
    "so", "well", "okay", "i mean",
]

# ── Pause / silence detection ─────────────────────────────────────────────────
SILENCE_TOP_DB      = 30    # dB below peak → considered silence (librosa)
MIN_PAUSE_DURATION  = 0.25  # seconds  – shorter gaps ignored

# ── Predefined reference concepts ─────────────────────────────────────────────
CONCEPTS = {
    "Machine Learning": (
        "Machine learning is a subset of artificial intelligence that enables systems "
        "to learn and improve from experience without being explicitly programmed. "
        "It focuses on developing algorithms that can access data, learn from it, "
        "and make predictions or decisions. Key types include supervised learning, "
        "unsupervised learning, and reinforcement learning. Common algorithms include "
        "linear regression, decision trees, neural networks, support vector machines, "
        "and clustering algorithms like K-means. Machine learning is used in image "
        "recognition, natural language processing, recommendation systems, fraud "
        "detection, and autonomous vehicles."
    ),
    "Deep Learning": (
        "Deep learning is a subfield of machine learning inspired by the structure "
        "and function of the human brain's neural networks. It uses multiple layers "
        "of artificial neurons to learn hierarchical representations of data. Deep "
        "learning excels at tasks such as image classification, speech recognition, "
        "and natural language understanding. Key architectures include convolutional "
        "neural networks (CNNs) for images, recurrent neural networks (RNNs) and "
        "transformers for sequential data, and generative adversarial networks (GANs) "
        "for data generation. Training requires large datasets and significant compute."
    ),
    "Cloud Computing": (
        "Cloud computing is the delivery of computing services including servers, "
        "storage, databases, networking, software, and analytics over the internet "
        "to offer faster innovation, flexible resources, and economies of scale. "
        "It is typically billed on a pay-as-you-go basis. The main service models "
        "are Infrastructure as a Service (IaaS), Platform as a Service (PaaS), and "
        "Software as a Service (SaaS). Deployment models include public, private, "
        "hybrid, and multi-cloud. Major providers include AWS, Microsoft Azure, "
        "and Google Cloud Platform. Benefits include scalability, cost reduction, "
        "disaster recovery, and global reach."
    ),
    "Artificial Intelligence": (
        "Artificial intelligence is the simulation of human intelligence processes "
        "by computer systems. It encompasses reasoning, learning, problem solving, "
        "perception, language understanding, and decision making. AI branches include "
        "machine learning, deep learning, natural language processing, computer vision, "
        "robotics, and expert systems. Narrow AI handles specific tasks while general "
        "AI aims for human-level cognition across all domains. AI applications include "
        "virtual assistants, autonomous vehicles, medical diagnosis, financial trading, "
        "and personalised recommendations. Ethical considerations include bias, privacy, "
        "transparency, and job displacement."
    ),
    "Natural Language Processing": (
        "Natural language processing (NLP) is a branch of artificial intelligence "
        "concerned with enabling computers to understand, interpret, and generate "
        "human language. It combines computational linguistics with machine learning "
        "and deep learning. Core NLP tasks include tokenisation, part-of-speech tagging, "
        "named entity recognition, sentiment analysis, machine translation, question "
        "answering, and text summarisation. Modern NLP relies on transformer architectures "
        "such as BERT and GPT. Applications include chatbots, voice assistants, "
        "sentiment monitoring, email filtering, and document summarisation."
    ),
    "Blockchain": (
        "Blockchain is a distributed, decentralised, and immutable digital ledger that "
        "records transactions across a network of computers. Each block contains a "
        "cryptographic hash of the previous block, a timestamp, and transaction data, "
        "forming a chain. Consensus mechanisms such as proof of work and proof of stake "
        "validate new blocks without a central authority. Key properties are transparency, "
        "security, and immutability. Applications include cryptocurrencies like Bitcoin "
        "and Ethereum, smart contracts, supply chain management, digital identity, "
        "healthcare records, and decentralised finance (DeFi)."
    ),
    "Internet of Things": (
        "The Internet of Things (IoT) refers to the network of physical objects embedded "
        "with sensors, software, and connectivity that enables them to collect and exchange "
        "data over the internet. IoT devices range from smart home appliances and wearables "
        "to industrial machinery and smart city infrastructure. Key components include "
        "sensors, connectivity protocols (Wi-Fi, Bluetooth, Zigbee, MQTT), cloud platforms, "
        "and data analytics. IoT enables remote monitoring, automation, predictive maintenance, "
        "and real-time decision making. Challenges include security vulnerabilities, "
        "interoperability, data privacy, and scalability."
    ),
    "Cybersecurity": (
        "Cybersecurity is the practice of protecting computer systems, networks, and data "
        "from digital attacks, unauthorised access, damage, and theft. It encompasses "
        "multiple domains including network security, application security, endpoint security, "
        "identity management, and data protection. Key threats include malware, phishing, "
        "ransomware, man-in-the-middle attacks, and denial-of-service attacks. Defence "
        "strategies include firewalls, encryption, multi-factor authentication, intrusion "
        "detection systems, and security audits. Frameworks like NIST and ISO 27001 guide "
        "organisational security posture. Cybersecurity is critical for businesses, "
        "governments, and individuals."
    ),
    "Data Science": (
        "Data science is an interdisciplinary field that uses scientific methods, algorithms, "
        "and systems to extract knowledge and insights from structured and unstructured data. "
        "It combines statistics, mathematics, programming, and domain expertise. The data "
        "science workflow includes data collection, cleaning, exploratory analysis, feature "
        "engineering, model building, evaluation, and deployment. Key tools include Python, "
        "R, SQL, Jupyter notebooks, Pandas, NumPy, Scikit-learn, and Tableau. Applications "
        "span healthcare analytics, financial modelling, marketing optimisation, and "
        "scientific research. Data scientists translate data into actionable business insights."
    ),
    "Operating Systems": (
        "An operating system is system software that manages computer hardware and software "
        "resources and provides common services for application programs. Core functions "
        "include process management, memory management, file system management, device "
        "management, and security. Key concepts include processes, threads, scheduling "
        "algorithms, virtual memory, paging, inter-process communication, and deadlocks. "
        "Popular operating systems include Windows, Linux, macOS, Android, and iOS. "
        "OS design involves trade-offs between performance, security, and usability. "
        "Modern OS support multiprocessing, multithreading, and virtualisation."
    ),
}

# ── Color palette (used in report PDF) ────────────────────────────────────────
COLOR_PRIMARY   = "#7C3AED"   # violet
COLOR_SECONDARY = "#06B6D4"   # cyan
COLOR_SUCCESS   = "#10B981"   # emerald
COLOR_WARNING   = "#F59E0B"   # amber
COLOR_DANGER    = "#EF4444"   # red
COLOR_BG        = "#0F0F1A"   # deep navy

# ── Allowed audio extensions ──────────────────────────────────────────────────
ALLOWED_EXTENSIONS = ["wav", "mp3", "m4a", "ogg", "flac", "webm"]

# ── Temp directory (relative) ─────────────────────────────────────────────────
TEMP_DIR = "temp"
