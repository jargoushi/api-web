"""账号服务"""

from typing import List, Optional

from app.core.exceptions import BusinessException
from app.core.logging import log
from app.enums.common.channel import ChannelEnum
from app.enums.common.project import ProjectEnum
from app.models.account.account import Account, AccountProjectChannel
from app.repositories.account.account_repository import account_repository
from app.repositories.account.binding_repository import account_project_channel_repository
from app.schemas.account.account import (
    AccountResponse,
    AccountCreateRequest,
    AccountUpdateRequest,
    BindingResponse,
    BindingRequest
)


class AccountService:
    """账号服务"""

    # ========== 账号管理 ==========

    async def get_accounts(self, user_id: int) -> List[AccountResponse]:
        """获取用户的所有账号"""
        log.info(f"用户{user_id}获取账号列表")
        accounts = await account_repository.find_by_user(user_id)
        return [self._to_account_response(acc) for acc in accounts]

    async def create_account(self, user_id: int, request: AccountCreateRequest) -> AccountResponse:
        """创建账号"""
        log.info(f"用户{user_id}创建账号: {request.name}")
        account = await account_repository.create(
            user_id=user_id,
            name=request.name,
            platform_account=request.platform_account,
            platform_password=request.platform_password,
            description=request.description
        )
        return self._to_account_response(account)

    async def update_account(self, user_id: int, request: AccountUpdateRequest) -> AccountResponse:
        """更新账号"""
        log.info(f"用户{user_id}更新账号{request.id}")
        account = await self._get_account_or_raise(request.id, user_id)

        if request.name is not None:
            account.name = request.name
        if request.platform_account is not None:
            account.platform_account = request.platform_account
        if request.platform_password is not None:
            account.platform_password = request.platform_password
        if request.description is not None:
            account.description = request.description

        await account.save()
        return self._to_account_response(account)

    async def delete_account(self, user_id: int, account_id: int) -> None:
        """删除账号（软删除）"""
        log.info(f"用户{user_id}删除账号{account_id}")
        account = await self._get_account_or_raise(account_id, user_id)
        await account_repository.soft_delete(account)

    # ========== 项目渠道绑定 ==========

    async def get_bindings(self, user_id: int, account_id: int) -> List[BindingResponse]:
        """获取账号的所有绑定"""
        log.info(f"获取账号{account_id}的绑定列表")
        await self._get_account_or_raise(account_id, user_id)

        bindings = await account_project_channel_repository.find_by_account(account_id)
        return [self._to_binding_response(b) for b in bindings]

    async def bindding(self, user_id: int, account_id: int, request: BindingRequest) -> BindingResponse:
        """绑定项目渠道"""
        log.info(f"账号{account_id}绑定项目{request.project_code}渠道{request.channel_code}")
        await self._get_account_or_raise(account_id, user_id)

        # 验证项目和渠道
        self._validate_project_channel(request.project_code, request.channel_code)

        binding = await account_project_channel_repository.upsert_binding(
            account_id=account_id,
            project_code=request.project_code,
            channel_code=request.channel_code,
            browser_id=request.browser_id
        )
        return self._to_binding_response(binding)

    async def update_binding(
        self, user_id: int, account_id: int, binding_id: int, browser_id: Optional[str]
    ) -> BindingResponse:
        """更新绑定（主要是浏览器ID）"""
        log.info(f"更新绑定{binding_id}的浏览器ID")
        await self._get_account_or_raise(account_id, user_id)

        binding = await account_project_channel_repository.get_by_id(binding_id)
        if not binding or binding.account_id != account_id:
            raise BusinessException(message="绑定不存在")

        binding.browser_id = browser_id
        await binding.save()
        return self._to_binding_response(binding)

    async def unbind(self, user_id: int, account_id: int, binding_id: int) -> None:
        """解绑"""
        log.info(f"解除绑定{binding_id}")
        await self._get_account_or_raise(account_id, user_id)

        binding = await account_project_channel_repository.get_by_id(binding_id)
        if not binding or binding.account_id != account_id:
            raise BusinessException(message="绑定不存在")

        await binding.delete()

    # ========== 辅助方法 ==========

    async def _get_account_or_raise(self, account_id: int, user_id: int) -> Account:
        """获取账号，不存在则抛异常"""
        account = await account_repository.find_by_id_and_user(account_id, user_id)
        if not account:
            raise BusinessException(message="账号不存在")
        return account

    def _validate_project_channel(self, project_code: int, channel_code: int) -> None:
        """验证项目是否支持该渠道"""
        try:
            project = ProjectEnum.from_code(project_code)
            channel = ChannelEnum.from_code(channel_code)
        except ValueError as e:
            raise BusinessException(message=str(e))

        if channel not in project.channels:
            raise BusinessException(message=f"项目{project.desc}不支持渠道{channel.desc}")

    def _to_account_response(self, account: Account) -> AccountResponse:
        """转换为响应对象"""
        return AccountResponse(
            id=account.id,
            name=account.name,
            platform_account=account.platform_account,
            platform_password=account.platform_password,
            description=account.description,
            created_at=account.created_at
        )

    def _to_binding_response(self, binding: AccountProjectChannel) -> BindingResponse:
        """转换为绑定响应对象"""
        project = ProjectEnum.from_code(binding.project_code)
        channel = ChannelEnum.from_code(binding.channel_code)
        return BindingResponse(
            id=binding.id,
            project_code=binding.project_code,
            project_name=project.desc,
            channel_code=binding.channel_code,
            channel_name=channel.desc,
            browser_id=binding.browser_id
        )


# 单例实例
account_service = AccountService()
