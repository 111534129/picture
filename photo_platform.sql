-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- 主機： 127.0.0.1
-- 產生時間： 2026-01-16 06:17:22
-- 伺服器版本： 10.4.32-MariaDB
-- PHP 版本： 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 資料庫： `photo_platform`
--

-- --------------------------------------------------------

--
-- 資料表結構 `albums`
--

CREATE TABLE `albums` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `title` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  `privacy` varchar(20) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `cover_id` int(11) DEFAULT NULL,
  `allow_download` tinyint(1) DEFAULT NULL,
  `is_banned` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `albums`
--

INSERT INTO `albums` (`id`, `user_id`, `title`, `description`, `privacy`, `created_at`, `cover_id`, `allow_download`, `is_banned`) VALUES
(1, 1, '小狗', '', 'public', '2025-12-27 13:34:25', 1, 0, NULL),
(2, 1, '貓', '', 'shared', '2025-12-27 14:12:20', NULL, NULL, NULL),
(3, 1, '派大星', '', 'private', '2025-12-28 10:10:31', NULL, NULL, NULL),
(4, 3, '123', '321', 'public', '2026-01-02 07:00:56', 6, 1, NULL),
(6, 3, '654', '#小狗', 'public', '2026-01-08 15:45:13', NULL, 1, 0);

-- --------------------------------------------------------

--
-- 資料表結構 `album_shares`
--

CREATE TABLE `album_shares` (
  `album_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `album_shares`
--

INSERT INTO `album_shares` (`album_id`, `user_id`) VALUES
(3, 2);

-- --------------------------------------------------------

--
-- 資料表結構 `alembic_version`
--

CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `alembic_version`
--

INSERT INTO `alembic_version` (`version_num`) VALUES
('5ce79742bc35');

-- --------------------------------------------------------

--
-- 資料表結構 `comments`
--

CREATE TABLE `comments` (
  `id` int(11) NOT NULL,
  `photo_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `content` text NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `parent_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `comments`
--

INSERT INTO `comments` (`id`, `photo_id`, `user_id`, `content`, `created_at`, `parent_id`) VALUES
(1, 1, 2, '好可愛喔', '2025-12-28 10:01:08', NULL),
(2, 1, 2, '嘻嘻嘻', '2025-12-28 10:05:17', 1),
(3, 5, 2, '好棒', '2026-01-07 03:07:33', NULL),
(4, 4, 2, '@123 快看', '2026-01-07 03:41:53', NULL),
(5, 5, 2, '@123', '2026-01-07 03:49:31', NULL);

-- --------------------------------------------------------

--
-- 資料表結構 `followers`
--

CREATE TABLE `followers` (
  `follower_id` int(11) NOT NULL,
  `followed_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `followers`
--

INSERT INTO `followers` (`follower_id`, `followed_id`) VALUES
(1, 2),
(2, 1),
(2, 3),
(3, 1);

-- --------------------------------------------------------

--
-- 資料表結構 `likes`
--

CREATE TABLE `likes` (
  `user_id` int(11) NOT NULL,
  `photo_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `likes`
--

INSERT INTO `likes` (`user_id`, `photo_id`, `created_at`) VALUES
(1, 6, '2026-01-07 02:58:23'),
(2, 4, '2026-01-07 02:50:11'),
(2, 5, '2026-01-07 03:07:27'),
(2, 8, '2026-01-14 01:45:07'),
(3, 1, '2026-01-07 03:08:06');

-- --------------------------------------------------------

--
-- 資料表結構 `notifications`
--

CREATE TABLE `notifications` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `author_id` int(11) DEFAULT NULL,
  `type` varchar(20) DEFAULT NULL,
  `payload` text DEFAULT NULL,
  `is_read` tinyint(1) DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `notifications`
--

INSERT INTO `notifications` (`id`, `user_id`, `author_id`, `type`, `payload`, `is_read`, `timestamp`) VALUES
(1, 3, 2, 'follow', '', 1, '2026-01-07 03:07:20'),
(2, 3, 2, 'like', '5', 1, '2026-01-07 03:07:27'),
(3, 3, 2, 'comment', '5', 1, '2026-01-07 03:07:33'),
(4, 1, 3, 'like', '1', 1, '2026-01-07 03:08:07'),
(5, 2, 1, 'new_photo', '1', 1, '2026-01-07 03:09:02'),
(6, 3, 1, 'new_photo', '1', 1, '2026-01-07 03:09:02'),
(7, 3, 2, 'comment', '4', 1, '2026-01-07 03:41:54'),
(8, 3, 2, 'comment', '5', 1, '2026-01-07 03:49:31'),
(9, 1, 2, 'mention', '5', 1, '2026-01-07 03:49:31'),
(10, 3, 1, 'system', '您的photo因違反社群規範（理由：其他：太爛）已被下架。', 1, '2026-01-08 15:08:59'),
(11, 2, 3, 'new_photo', '4', 1, '2026-01-08 15:44:26'),
(12, 2, 3, 'new_album', '6', 1, '2026-01-08 15:45:14'),
(13, 2, 3, 'new_photo', '6', 1, '2026-01-08 15:45:26'),
(17, 3, 1, 'system', '您的照片「螢幕擷取畫面 2026-01-08 234116.png」因違反社群規範（理由：其他：太爛）已被下架。', 1, '2026-01-09 07:04:51'),
(18, 1, 2, 'like', '8', 1, '2026-01-14 01:45:07');

-- --------------------------------------------------------

--
-- 資料表結構 `photos`
--

CREATE TABLE `photos` (
  `id` int(11) NOT NULL,
  `album_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `filename` varchar(255) NOT NULL,
  `original_filename` varchar(255) NOT NULL,
  `filesize` int(11) DEFAULT NULL,
  `taken_at` datetime DEFAULT NULL,
  `uploaded_at` datetime DEFAULT NULL,
  `position` int(11) DEFAULT NULL,
  `is_banned` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `photos`
--

INSERT INTO `photos` (`id`, `album_id`, `user_id`, `filename`, `original_filename`, `filesize`, `taken_at`, `uploaded_at`, `position`, `is_banned`) VALUES
(1, 1, 1, '9363efa5-7f85-4d0f-ad8e-bf82200ebef7.JPG', '1.JPG', 60693, NULL, '2025-12-27 13:36:39', NULL, NULL),
(2, 2, 1, 'a424d007-a8fa-465a-bb1e-2eaa799055e4.jpg', '3.jpg', 64695, NULL, '2025-12-27 14:12:24', NULL, NULL),
(3, 3, 1, 'f52ef1a3-a9cf-47f5-92e3-15753304b1af.jpeg', '4.jpeg', 28018, NULL, '2025-12-28 10:10:36', NULL, NULL),
(4, 4, 3, 'a0f9e5d8-d456-4f10-a974-83cb0fb2095c.png', '螢幕擷取畫面 2025-10-12 163836.png', 50257, NULL, '2026-01-02 07:01:19', 3, NULL),
(5, 4, 3, 'f9fa6187-2bd0-4c86-9b69-f4b9f628f210.png', '螢幕擷取畫面 2025-10-12 164143.png', 407641, NULL, '2026-01-02 07:01:19', 2, NULL),
(6, 4, 3, '92ea7af1-5482-407f-951c-6dc92c007a4e.png', '螢幕擷取畫面 2025-10-12 164815.png', 54297, NULL, '2026-01-02 07:01:19', 1, 1),
(7, 4, 3, 'fe3fd325-71a6-4df0-88f3-ad4fe3dab50f.png', '螢幕擷取畫面 2025-10-12 165923.png', 15848, NULL, '2026-01-02 07:01:19', 0, NULL),
(8, 1, 1, 'd1af5793-27f7-4f58-9cc5-633304c1f3bb.png', '螢幕擷取畫面 2025-10-12 174202.png', 87360, NULL, '2026-01-07 03:09:01', NULL, NULL),
(9, 1, 1, '585846c5-ec18-4588-8794-097a68d4b68b.png', '螢幕擷取畫面 2025-10-19 213404.png', 71850, NULL, '2026-01-07 03:09:01', NULL, NULL),
(10, 1, 1, '5b673cbd-1252-4de4-9806-1bdebe3dbb10.png', '螢幕擷取畫面 2025-11-04 140952.png', 58817, NULL, '2026-01-07 03:09:01', NULL, NULL),
(11, 1, 1, '5089325e-d578-4345-a208-6f845f039860.png', '螢幕擷取畫面 2025-11-04 151615.png', 22762, NULL, '2026-01-07 03:09:02', NULL, NULL),
(16, 4, 3, '358c9d8e-f69e-42de-9c85-781912ee1827.png', '螢幕擷取畫面 2026-01-08 234116.png', 144328, NULL, '2026-01-08 15:44:26', 0, 0),
(17, 6, 3, '825a5710-90b7-4268-b0ff-43c0c1321067.png', '螢幕擷取畫面 2026-01-08 234116.png', 144328, NULL, '2026-01-08 15:45:26', 0, 1),
(18, 6, 3, '79b81c49-95f2-4e08-a5df-f59dc6936c6e.png', '螢幕擷取畫面 2026-01-08 232109.png', 294722, NULL, '2026-01-08 15:45:26', 0, 0),
(19, 6, 3, 'ba94e84b-fe57-491f-90f1-105e939d002b.png', '螢幕擷取畫面 2026-01-08 230953.png', 309125, NULL, '2026-01-08 15:45:26', 0, 0);

-- --------------------------------------------------------

--
-- 資料表結構 `photo_tags`
--

CREATE TABLE `photo_tags` (
  `photo_id` int(11) NOT NULL,
  `tag_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `photo_tags`
--

INSERT INTO `photo_tags` (`photo_id`, `tag_id`) VALUES
(17, 1),
(17, 2),
(18, 1),
(19, 1);

-- --------------------------------------------------------

--
-- 資料表結構 `reports`
--

CREATE TABLE `reports` (
  `id` int(11) NOT NULL,
  `reporter_id` int(11) NOT NULL,
  `target_type` varchar(20) NOT NULL,
  `target_id` int(11) NOT NULL,
  `reason` varchar(255) NOT NULL,
  `status` varchar(20) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `reports`
--

INSERT INTO `reports` (`id`, `reporter_id`, `target_type`, `target_id`, `reason`, `status`, `created_at`) VALUES
(1, 2, 'photo', 7, '其他', 'dismissed', '2026-01-08 14:53:23'),
(2, 2, 'photo', 6, '其他：太爛', 'resolved', '2026-01-08 15:03:44'),
(4, 2, 'photo', 28, '色情或裸露內容', 'resolved', '2026-01-14 01:52:54');

-- --------------------------------------------------------

--
-- 資料表結構 `tags`
--

CREATE TABLE `tags` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `tags`
--

INSERT INTO `tags` (`id`, `name`, `created_at`) VALUES
(1, '小狗', '2026-01-08 15:45:26'),
(2, '5', '2026-01-09 05:54:27'),
(3, '許光漢好帥', '2026-01-09 07:02:21');

-- --------------------------------------------------------

--
-- 資料表結構 `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(64) NOT NULL,
  `email` varchar(120) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `avatar` varchar(200) DEFAULT NULL,
  `intro` text DEFAULT NULL,
  `role` varchar(20) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `liked_photos_privacy` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `users`
--

INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `avatar`, `intro`, `role`, `created_at`, `liked_photos_privacy`) VALUES
(1, '123', '123@gmail.com', 'scrypt:32768:8:1$vrUkgtTXcMpxg0hs$14e4e2a0fcc4d1466c7d1275bef4138c2b18142ea9857f2403c8887f05c0fc130700144f5f061137394567564aff384296828e80574be9a23920513af7740754', 'c562c9c5-7a30-44ef-83af-5f5512112564.jpg', '哈囉', 'admin', '2025-12-27 13:33:49', 'public'),
(2, '456', '456@gmail.com', 'scrypt:32768:8:1$CM6oUrUm6Pmphnki$5b368753f193845c4f6ccdc67885fe07da931ddc2047313d19680780a432c847e7efb74e8e6e212e2e52d398df42765c836eb13d220fe5bb0bc303c5939bf93e', NULL, '', 'user', '2025-12-27 14:10:52', 'private'),
(3, '789', '789@gmail.com', 'scrypt:32768:8:1$Xaf01u2FYJeTs9rw$3da6c8546751b6a19f9a079a3a260fdb5738bd2923b8947c625d5c50d4b3194e2b6fe3c58d1766689e2821e17fa089d8af3c7edcc5dfcd0779b38209338ed832', NULL, NULL, 'user', '2026-01-02 07:00:10', NULL);

--
-- 已傾印資料表的索引
--

--
-- 資料表索引 `albums`
--
ALTER TABLE `albums`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `fk_album_cover_photo` (`cover_id`);

--
-- 資料表索引 `album_shares`
--
ALTER TABLE `album_shares`
  ADD PRIMARY KEY (`album_id`,`user_id`),
  ADD KEY `user_id` (`user_id`);

--
-- 資料表索引 `alembic_version`
--
ALTER TABLE `alembic_version`
  ADD PRIMARY KEY (`version_num`);

--
-- 資料表索引 `comments`
--
ALTER TABLE `comments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `photo_id` (`photo_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `parent_id` (`parent_id`);

--
-- 資料表索引 `followers`
--
ALTER TABLE `followers`
  ADD PRIMARY KEY (`follower_id`,`followed_id`),
  ADD KEY `followed_id` (`followed_id`);

--
-- 資料表索引 `likes`
--
ALTER TABLE `likes`
  ADD PRIMARY KEY (`user_id`,`photo_id`),
  ADD KEY `photo_id` (`photo_id`);

--
-- 資料表索引 `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `author_id` (`author_id`),
  ADD KEY `ix_notifications_timestamp` (`timestamp`),
  ADD KEY `ix_notifications_user_id` (`user_id`);

--
-- 資料表索引 `photos`
--
ALTER TABLE `photos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `album_id` (`album_id`),
  ADD KEY `user_id` (`user_id`);

--
-- 資料表索引 `photo_tags`
--
ALTER TABLE `photo_tags`
  ADD PRIMARY KEY (`photo_id`,`tag_id`),
  ADD KEY `tag_id` (`tag_id`);

--
-- 資料表索引 `reports`
--
ALTER TABLE `reports`
  ADD PRIMARY KEY (`id`),
  ADD KEY `reporter_id` (`reporter_id`);

--
-- 資料表索引 `tags`
--
ALTER TABLE `tags`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ix_tags_name` (`name`);

--
-- 資料表索引 `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ix_users_email` (`email`),
  ADD UNIQUE KEY `ix_users_username` (`username`);

--
-- 在傾印的資料表使用自動遞增(AUTO_INCREMENT)
--

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `albums`
--
ALTER TABLE `albums`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `comments`
--
ALTER TABLE `comments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `notifications`
--
ALTER TABLE `notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `photos`
--
ALTER TABLE `photos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=33;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `reports`
--
ALTER TABLE `reports`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `tags`
--
ALTER TABLE `tags`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- 已傾印資料表的限制式
--

--
-- 資料表的限制式 `albums`
--
ALTER TABLE `albums`
  ADD CONSTRAINT `albums_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `fk_album_cover_photo` FOREIGN KEY (`cover_id`) REFERENCES `photos` (`id`);

--
-- 資料表的限制式 `album_shares`
--
ALTER TABLE `album_shares`
  ADD CONSTRAINT `album_shares_ibfk_1` FOREIGN KEY (`album_id`) REFERENCES `albums` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `album_shares_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- 資料表的限制式 `comments`
--
ALTER TABLE `comments`
  ADD CONSTRAINT `comments_ibfk_1` FOREIGN KEY (`photo_id`) REFERENCES `photos` (`id`),
  ADD CONSTRAINT `comments_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `comments_ibfk_3` FOREIGN KEY (`parent_id`) REFERENCES `comments` (`id`);

--
-- 資料表的限制式 `followers`
--
ALTER TABLE `followers`
  ADD CONSTRAINT `followers_ibfk_1` FOREIGN KEY (`followed_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `followers_ibfk_2` FOREIGN KEY (`follower_id`) REFERENCES `users` (`id`);

--
-- 資料表的限制式 `likes`
--
ALTER TABLE `likes`
  ADD CONSTRAINT `likes_ibfk_1` FOREIGN KEY (`photo_id`) REFERENCES `photos` (`id`),
  ADD CONSTRAINT `likes_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- 資料表的限制式 `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `notifications_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- 資料表的限制式 `photos`
--
ALTER TABLE `photos`
  ADD CONSTRAINT `photos_ibfk_1` FOREIGN KEY (`album_id`) REFERENCES `albums` (`id`),
  ADD CONSTRAINT `photos_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- 資料表的限制式 `photo_tags`
--
ALTER TABLE `photo_tags`
  ADD CONSTRAINT `photo_tags_ibfk_1` FOREIGN KEY (`photo_id`) REFERENCES `photos` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `photo_tags_ibfk_2` FOREIGN KEY (`tag_id`) REFERENCES `tags` (`id`) ON DELETE CASCADE;

--
-- 資料表的限制式 `reports`
--
ALTER TABLE `reports`
  ADD CONSTRAINT `reports_ibfk_1` FOREIGN KEY (`reporter_id`) REFERENCES `users` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
