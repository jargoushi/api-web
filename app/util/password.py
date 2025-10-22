import bcrypt


def hash_password(password: str) -> str:
    """
    使用 bcrypt 库对密码进行哈希处理。
    """
    # bcrypt 库要求密码必须是 bytes 类型
    password_bytes = password.encode('utf-8')

    # gensalt() 生成一个随机的盐
    salt = bcrypt.gensalt()

    # hashpw() 进行哈希，返回的也是 bytes
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)

    # 将结果解码回字符串存储
    return hashed_bytes.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码。
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')

    # checkpw 会自动从哈希值中提取盐进行验证
    return bcrypt.checkpw(password_bytes, hashed_bytes)
