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
    AccountQueryRequest,
    BindingResponse,
    BindingRequest,
    BindingUpdateRequest
)


class AccountService:
    """账号服务"""

    # ========== 账号管理 ==========

    def get_account_queryset(self, params: AccountQueryRequest):
        """获取账号查询集（用于分页）"""
        query = Account.all()

        # 按用户筛选
        if params.user_id:
            query = query.filter(user_id=params.user_id)

        # 按名称模糊搜索
        if params.name:
            query = query.filter(name__icontains=params.name)

        return query.order_by("-created_at")

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

    async def update_account(self, request: AccountUpdateRequest) -> AccountResponse:
        """更新账号"""
        log.info(f"更新账号{request.id}")
        account = await Account.get_or_none(id=request.id)
        if not account:
            raise BusinessException(message="账号不存在", code=404)

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

    async def delete_account(self, account_id: int) -> None:
        """删除账号"""
        log.info(f"删除账号{account_id}")
        account = await Account.get_or_none(id=account_id)
        if not account:
            raise BusinessException(message="账号不存在", code=404)
        await account.delete()

    # ========== 项目渠道绑定 ==========

    async def get_bindings(self, account_id: int) -> List[BindingResponse]:
        """获取账号的所有绑定"""
        log.info(f"获取账号{account_id}的绑定列表")
        bindings = await AccountProjectChannel.filter(account_id=account_id)
        return [self._to_binding_response(b) for b in bindings]

    async def bindding(self, account_id: int, request: BindingRequest) -> BindingResponse:
        """绑定项目渠道"""
        log.info(f"账号{account_id}绑定项目{request.project_code}渠道{request.channel_codes}")

        # 验证项目和渠道
        self._validate_project_channels(request.project_code, request.channel_codes)

        # 查找或创建绑定
        channel_codes_str = ",".join(str(c) for c in request.channel_codes)
        binding = await AccountProjectChannel.get_or_none(
            account_id=account_id, project_code=request.project_code
        )

        if binding:
            binding.channel_codes = channel_codes_str
            binding.browser_id = request.browser_id
            await binding.save()
        else:
            binding = await AccountProjectChannel.create(
                account_id=account_id,
                project_code=request.project_code,
                channel_codes=channel_codes_str,
                browser_id=request.browser_id
            )

        return self._to_binding_response(binding)

    async def update_binding(self, request: BindingUpdateRequest) -> BindingResponse:
        """更新绑定"""
        log.info(f"更新绑定{request.id}")
        binding = await AccountProjectChannel.get_or_none(id=request.id)
        if not binding:
            raise BusinessException(message="绑定不存在", code=404)

        if request.channel_codes is not None:
            self._validate_project_channels(binding.project_code, request.channel_codes)
            binding.channel_codes = ",".join(str(c) for c in request.channel_codes)
        if request.browser_id is not None:
            binding.browser_id = request.browser_id

        await binding.save()
        return self._to_binding_response(binding)

    async def unbind(self, binding_id: int) -> None:
        """解绑"""
        log.info(f"解除绑定{binding_id}")
        binding = await AccountProjectChannel.get_or_none(id=binding_id)
        if not binding:
            raise BusinessException(message="绑定不存在", code=404)
        await binding.delete()

    # ========== 辅助方法 ==========

    def _validate_project_channels(self, project_code: int, channel_codes: List[int]) -> None:
        """验证项目是否支持这些渠道"""
        try:
            project = ProjectEnum.from_code(project_code)
        except ValueError as e:
            raise BusinessException(message=str(e))

        for channel_code in channel_codes:
            try:
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
        channel_codes = [int(c) for c in binding.channel_codes.split(",") if c]
        channel_names = [ChannelEnum.from_code(c).desc for c in channel_codes]

        return BindingResponse(
            id=binding.id,
            project_code=binding.project_code,
            project_name=project.desc,
            channel_codes=channel_codes,
            channel_names=channel_names,
            browser_id=binding.browser_id
        )


# 单例实例
account_service = AccountService()
