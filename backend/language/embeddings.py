import numpy as np
from sentence_transformers import SentenceTransformer

COMMANDS = [
    "Go to the red cylinder at the far end.",
    "Navigate toward the distant red cylindrical object.",
    "Stop at the blue box",
    "前往远处的红色圆柱体。",
    "走到远处的红色圆筒形物体",
    "Направляйтесь к красному цилиндру вдалеке.",
    "به سمت استوانه قرمز در دوردست بروید.",
    "멀리 있는 붉은 원통으로 가라.",
]

def main() -> None:
    model = SentenceTransformer(
        "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    )

    # 正则化向量中的数据
    embeddings = model.encode(
        COMMANDS,
        normalize_embeddings=True,
    )

    # 正则化向量后，点积 余弦 (cos) 相似度
    similarity_matrix = np.matmul(embeddings, embeddings.T)

    print("Commands:\n")

    # 每行命令必须以 索引:命令 形式输出的
    for index, command in enumerate(COMMANDS):
        print(f"{index}: {command}")

    print("\nSimilarity matrix:\n")
    print(np.round(similarity_matrix, 3))

    print(
        "\nSimilar pair:",
        similarity_matrix[0,1],
        COMMANDS[0],
        "<->",
        COMMANDS[1],
    )

    print(
        "\nDissimilar pair:",
        similarity_matrix[0,2],
        COMMANDS[0],
        "<->",
        COMMANDS[2],
    )

    print(
        "\nCross-language pair:",
        similarity_matrix[3,6],
        COMMANDS[3],
        "<->",
        COMMANDS[6],
        )

if __name__ == "__main__":
    main()