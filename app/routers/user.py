from app.models.user import User
from fastapi import APIRouter, status
from tortoise.exceptions import IntegrityError

from app.schemas.response import success_response, error_response
from app.schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.post("/", response_model=dict)
async def create_user(user_data: UserCreate):
    """创建用户"""
    try:
        # 这里应该对密码进行哈希处理，简化示例省略
        user = await User.create(
            username=user_data.username,
            email=user_data.email,
            hashed_password="hashed_" + user_data.password  # 实际应用中应该使用 bcrypt
        )
        return success_response(
            data=await UserResponse.from_tortoise_orm(user),
            message="用户创建成功"
        )
    except IntegrityError:
        return error_response(
            message="用户名或邮箱已存在",
            code=status.HTTP_400_BAD_REQUEST
        )


@router.get("/{user_id}", response_model=dict)
async def get_user(user_id: int):
    """获取单个用户"""
    user = await User.get_or_none(id=user_id)
    if not user:
        return error_response(
            message="用户不存在",
            code=status.HTTP_404_NOT_FOUND
        )

    return success_response(
        data=await UserResponse.from_tortoise_orm(user)
    )


@router.get("/", response_model=dict)
async def list_users():
    """获取用户列表"""
    users = await User.all()
    user_list = [await UserResponse.from_tortoise_orm(user) for user in users]

    return success_response(
        data=user_list,
        message="用户列表查询成功"
    )


@router.put("/{user_id}", response_model=dict)
async def update_user(user_id: int, user_data: UserUpdate):
    """更新用户"""
    user = await User.get_or_none(id=user_id)
    if not user:
        return error_response(
            message="用户不存在",
            code=status.HTTP_404_NOT_FOUND
        )

    update_data = user_data.dict(exclude_unset=True)
    if update_data:
        await user.update_from_dict(update_data)
        await user.save()

    return success_response(
        data=await UserResponse.from_tortoise_orm(user),
        message="用户更新成功"
    )


@router.delete("/{user_id}", response_model=dict)
async def delete_user(user_id: int):
    """删除用户"""
    user = await User.get_or_none(id=user_id)
    if not user:
        return error_response(
            message="用户不存在",
            code=status.HTTP_404_NOT_FOUND
        )

    await user.delete()
    return success_response(
        data={"deleted": True},
        message="用户删除成功"
    )
