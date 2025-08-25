# 統一的 API請求限制

# 單次請求總大小（bytes）
MAX_PAYLOAD_BYTES = 1_000_000  # 1MB

# 聊天訊息與歷史限制
MESSAGE_MAX_CHARS = 4000
# 將記憶上限提升，滿足使用者在刷新前的長對話需求
HISTORY_MAX_TURNS = 30
HISTORY_ITEM_MAX_CHARS = 4000
TOTAL_HISTORY_MAX_CHARS = 20000

# RAG retrieval tuning
RETRIEVAL_MAX_SOURCES = 5
# Keep candidates within (1 + RELATIVE_EPS) * best_distance
RETRIEVAL_RELATIVE_DISTANCE_EPS = 0.2


