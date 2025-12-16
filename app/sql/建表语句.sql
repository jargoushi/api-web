-- 激活码表
CREATE TABLE `activation_codes` (
    `id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT '激活码ID',
    `activation_code` varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '激活码',
    `distributed_at` datetime DEFAULT NULL COMMENT '分发时间',
    `activated_at` datetime DEFAULT NULL COMMENT '激活时间',
    `expire_time` datetime DEFAULT NULL COMMENT '过期时间',
    `type` int unsigned NOT NULL COMMENT '激活码类型',
    `status` int unsigned NOT NULL DEFAULT '0' COMMENT '激活码状态 0:未使用 1:已分发 2:已激活',
    `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`) USING BTREE,
    UNIQUE KEY `uk_activation_code` (`activation_code`) USING BTREE,
    KEY `idx_status` (`status`) USING BTREE,
    KEY `idx_type` (`type`) USING BTREE,
    KEY `idx_created_at` (`created_at`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='激活码表';


-- 用户表
CREATE TABLE `user` (
    `id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT '用户ID',
    `username` varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '用户名',
    `password` varchar(128) COLLATE utf8mb4_general_ci NOT NULL COMMENT '密码',
    `phone` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '手机号',
    `email` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '邮箱',
    `activation_code` varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '激活码',
    `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`) USING BTREE,
    UNIQUE KEY `uk_username` (`username`) USING BTREE,
    UNIQUE KEY `uk_phone` (`phone`) USING BTREE,
    UNIQUE KEY `uk_email` (`email`) USING BTREE,
    KEY `idx_activation_code` (`activation_code`) USING BTREE,
    KEY `idx_created_at` (`created_at`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='用户表';

CREATE TABLE `monitor_configs` (
	`id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
	`user_id` BIGINT UNSIGNED NOT NULL COMMENT '所属用户ID',
	`channel_code` INT UNSIGNED NOT NULL COMMENT '渠道编码 (对应 ChannelEnum)',
	`target_url` VARCHAR ( 512 ) COLLATE utf8mb4_general_ci NOT NULL COMMENT '监控目标链接',
	`target_external_id` VARCHAR ( 128 ) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '平台唯一ID (如B站mid, YouTube ChannelID)',
	`account_name` VARCHAR ( 128 ) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '账号名称快照',
	`account_avatar` VARCHAR ( 512 ) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '账号头像URL',
	`is_active` TINYINT UNSIGNED NOT NULL DEFAULT '1' COMMENT '是否启用监控 0:否 1:是',
	`last_run_at` DATETIME DEFAULT NULL COMMENT '上次任务执行时间',
	`last_run_status` TINYINT UNSIGNED DEFAULT NULL COMMENT '上次执行结果 0:失败 1:成功',
	`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
	`updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
	`deleted_at` DATETIME DEFAULT NULL COMMENT '删除时间 (软删除)',
	PRIMARY KEY ( `id` ) USING BTREE,
	KEY `idx_user_id` ( `user_id` ) USING BTREE,
	KEY `idx_channel_code` ( `channel_code` ) USING BTREE
) ENGINE = INNODB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC COMMENT = '监控配置主表';

CREATE TABLE `monitor_daily_stats` (
	`id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
	`config_id` BIGINT UNSIGNED NOT NULL COMMENT '关联配置ID',
	`stat_date` DATE NOT NULL COMMENT '统计日期 (YYYY-MM-DD)',
	`follower_count` INT UNSIGNED NOT NULL DEFAULT '0' COMMENT '粉丝数',
	`liked_count` INT UNSIGNED NOT NULL DEFAULT '0' COMMENT '获赞/收藏数',
	`view_count` BIGINT UNSIGNED NOT NULL DEFAULT '0' COMMENT '总播放/阅读量',
	`content_count` INT UNSIGNED NOT NULL DEFAULT '0' COMMENT '发布内容数量',
	`extra_data` JSON DEFAULT NULL COMMENT '渠道特有数据 (如B站硬币, 小红书笔记数)',
	`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '数据入库时间',
	`updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
	PRIMARY KEY ( `id` ) USING BTREE,
	UNIQUE KEY `uk_config_date` ( `config_id`, `stat_date` ) USING BTREE COMMENT '确保每日每配置只有一条记录',
	KEY `idx_stat_date` ( `stat_date` ) USING BTREE
) ENGINE = INNODB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC COMMENT = '监控每日数据明细表';

CREATE TABLE `tasks` (
	`id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '任务ID',
	`channel_code` INT UNSIGNED NOT NULL COMMENT '渠道编码 (ChannelEnum)',
	`task_type` INT UNSIGNED NOT NULL COMMENT '任务类型 (TaskTypeEnum)',
	`biz_id` BIGINT UNSIGNED NOT NULL COMMENT '业务ID (关联 monitor_configs.id)',
	`task_status` TINYINT UNSIGNED NOT NULL DEFAULT '0' COMMENT '状态 1:进行中 2:成功 3:失败',
	`schedule_date` DATE NOT NULL COMMENT '调度日期 (标识这是哪一天的任务)',
	`error_msg` TEXT COLLATE utf8mb4_general_ci COMMENT '异常信息栈',
	`duration_ms` INT UNSIGNED DEFAULT '0' COMMENT '耗时(ms)',
	`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '任务创建时间',
	`updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
	`started_at` DATETIME DEFAULT NULL COMMENT '开始执行时间',
	`finished_at` DATETIME DEFAULT NULL COMMENT '结束执行时间',
	PRIMARY KEY ( `id` ) USING BTREE,
	KEY `idx_biz_id` ( `biz_id` ) USING BTREE,
	KEY `idx_schedule` ( `schedule_date`, `task_type`, `task_status` ) USING BTREE COMMENT '查询某天某类任务执行情况',
	KEY `idx_created` ( `created_at` ) USING BTREE
) ENGINE = INNODB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC COMMENT = '任务表';

-- 用户配置表
CREATE TABLE `user_settings` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    `setting_key` INT UNSIGNED NOT NULL COMMENT '配置项编码 (对应 SettingKeyEnum)',
    `setting_value` JSON NOT NULL COMMENT '配置值',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`) USING BTREE,
    UNIQUE KEY `uk_user_key` (`user_id`, `setting_key`) USING BTREE COMMENT '每用户每配置项唯一',
    KEY `idx_user_id` (`user_id`) USING BTREE
) ENGINE = INNODB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC COMMENT = '用户配置表';
