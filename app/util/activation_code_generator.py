"""
激活码生成工具类
"""
import hashlib
import secrets
import string


class ActivationCodeGenerator:
    """
    激活码生成器

    负责生成随机的激活码字符串
    """

    @staticmethod
    def generate() -> str:
        """
        生成随机激活码

        生成规则：
        1. 生成32位随机种子
        2. 使用SHA256进行第一次哈希
        3. 使用MD5进行第二次哈希（取前32位）
        4. 添加16位随机后缀

        Returns:
            str: 48位激活码字符串
        """
        # 生成随机种子
        seed = ''.join(
            secrets.choice(string.ascii_letters + string.digits)
            for _ in range(32)
        )

        # 第一次哈希：SHA256
        hash1 = hashlib.sha256(seed.encode()).hexdigest()

        # 第二次哈希：MD5（取前32位）
        hash2 = hashlib.md5(hash1.encode()).hexdigest()

        # 生成后缀
        suffix_chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
        suffix = ''.join(
            secrets.choice(suffix_chars)
            for _ in range(16)
        )

        return f"{hash2}{suffix}"


code_generator = ActivationCodeGenerator()
