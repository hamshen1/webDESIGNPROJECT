# Project Technical Specification

## Overview

This project involves creating a **personalized news website** that progressively adjusts content extremity for users based on their behavior, preferences, and engagement history. The platform serves articles ranging from factual to increasingly extreme and fabricated, intended to subtly shift user perceptions over time. The design emphasizes a seamless, responsive user experience and personalized content recommendations.

## Table of Contents

1. [Technology Stack](#technology-stack)
2. [Frontend Structure](#frontend-structure)
   - [Home Page Components](#home-page-components)
   - [User Profile Components](#user-profile-components)
   - [Notification Center Components](#notification-center-components)
   - [Login and Registration Components](#login-and-registration-components)
   - [Settings and Personalization Components](#settings-and-personalization-components)
3. [Backend Structure](#backend-structure)
   - [User Management](#user-management)
   - [Content Management](#content-management)
   - [Profiling and Tailoring Algorithm](#profiling-and-tailoring-algorithm)
4. [Frontend-to-Backend Interactions](#frontend-to-backend-interactions)
5. [Figma Mapping Guide](#figma-mapping-guide)

---

## Technology Stack

- **Frontend:** ReactJS, Redux, HTML5, CSS3
- **Backend:** Node.js, Express, MongoDB, Redis, Python for profiling algorithms
- **Authentication:** Firebase Authentication or Auth0
- **Notification System:** Firebase Cloud Messaging (for web push notifications)
- **Tracking & Analytics:** Google Analytics, Mixpanel

---

## Frontend Structure

### Home Page Components

#### `HomePage.js`

- **Description:** Container for the homepage layout, handling data loading and state management.
- **State Management:** Manages data loading for `TopHeadlinesSection`, `CurrentTopicsSection`, and `MiscContentSection`.
- **Key Interactions:**
  - **Initial Data Load:** Requests article data from backend upon initial render.
  - **Conditional Rendering:** Displays loading spinners or placeholders while fetching data.
  - **Behavior:** Renders each section (headlines, current topics, miscellaneous content) and passes relevant data as props.

#### `TopHeadlinesSection.js`

- **Description:** Displays the top three articles selected for the user, each with a title, background image, and short summary.
- **Props:** `topHeadlines` (Array of article objects containing `title`, `summary`, `imageURL`, `articleID`)
- **Key Interactions:**
  - **Data Fetch:** Retrieves top headline articles via `GET /articles` endpoint from `articleRoutes.js`.
  - **User Engagement:** Clicking a headline triggers an event to update engagement metrics via Redux state and backend.
  - **Responsive Design:** Uses CSS flex or grid layout to ensure headlines scale correctly on different screen sizes.

#### `CurrentTopicsSection.js`

- **Description:** Displays a row of clickable topics based on current trends or the user’s interests.
- **Props:** `currentTopics` (Array of topic strings)
- **Key Interactions:**
  - **Data Fetch:** Queries articles filtered by selected topic via `GET /articles?tags=...`.
  - **User Engagement:** Tracks topic interactions, updates backend with user preferences when a topic is clicked.

#### `MiscContentSection.js`

- **Description:** Section for displaying general interest content that’s not highly personalized, like stock market data or non-targeted articles.
- **Props:** `miscArticles` (Array of general article objects)
- **Key Interactions:**
  - **Data Fetch:** Pulls non-personalized articles or financial data from backend.
  - **Behavior:** Links articles or data points to non-personalized content, with limited backend interaction.

#### `NotificationBell.js`

- **Description:** Notification icon showing the number of unread notifications.
- **State Management:** Maintains `unreadCount` to reflect the number of new notifications.
- **Key Interactions:**
  - **Notification Fetch:** Uses `GET /notifications` to fetch unread notifications on page load.
  - **Behavior:** Clicking the bell opens `NotificationCenter` to view all notifications and marks them as read.

### User Profile Components

#### `UserProfile.js`

- **Description:** Container for the user profile page, displaying metrics, streaks, and achievements.
- **State Management:** Manages `userProfileData`, `streakCount`, `badgeAchievements`, and other personalized stats.
- **Key Interactions:**
  - **Data Fetch:** Retrieves user profile data using `GET /personalData` from backend.
  - **Conditional Rendering:** Shows skeleton loaders while fetching profile data.
  - **Behavior:** Displays `ProfileStreakCounter`, `BadgeDisplay`, `EngagementStats`, and other components based on user data.

#### `ProfileStreakCounter.js`

- **Description:** Displays the user’s consecutive day streak of engagement.
- **Props:** `userStreak` (Integer representing the streak count)
- **Key Interactions:**
  - **Streak Update:** Updates engagement metrics by calling `POST /updateMetrics` in `userRoutes.js`.
  - **Milestone Detection:** Tracks streak milestones (e.g., 7 days) to award badges via Redux or backend.

#### `BadgeDisplay.js`

- **Description:** Shows a collection of badges the user has earned for engagement.
- **Props:** `badgeAchievements` (Array of badge names)
- **Key Interactions:**
  - **Badge Fetch:** Pulls badge data from `userProfileData` on initial render.
  - **Behavior:** Clicking a badge icon shows additional details about the achievement in a tooltip or modal.

#### `RankingPosition.js`

- **Description:** Displays the user's rank or engagement level compared to other users.
- **Props:** `rankingPosition` (String indicating the rank)
- **Key Interactions:**
  - **Data Fetch:** Renders based on `rankingPosition` retrieved via `GET /personalData`.
  - **User Feedback:** Provides UI feedback if the user’s rank increases, showing a congratulatory animation or popup.

### Notification Center Components

#### `NotificationCenter.js`

- **Description:** Main notification area showing a list of recent notifications.
- **State Management:** Manages an array `notifications` with recent notification data.
- **Key Interactions:**
  - **Data Fetch:** Uses `GET /notifications` to load recent notifications on component mount.
  - **Conditional Behavior:** Shows “No new notifications” if `notifications` array is empty.
  - **Interaction:** Clicking a notification marks it as read, updating both Redux and backend.

#### `NotificationItem.js`

- **Description:** Individual notification entry in the list.
- **Props:** `notification` (Object containing `title`, `message`, `timestamp`, `isRead`)
- **Key Interactions:**
  - **Mark as Read:** Calls backend `POST /markRead` to mark notifications as read when clicked.
  - **UI Feedback:** Applies a “read” styling to dim the notification once clicked.

#### `MarkAllAsReadButton.js`

- **Description:** Button allowing the user to mark all notifications as read.
- **Interactions:**
  - **Backend Update:** Sends `POST /markAllRead` request to backend to mark all notifications as read.
  - **UI Feedback:** Clears unread count in `NotificationBell.js` and dims all notifications.

### Login and Registration Components

#### `LoginModal.js`

- **Description:** Login modal for user authentication.
- **State Management:** Manages input fields `username`, `password`, and error messages.
- **Key Interactions:**
  - **Authentication:** Sends login request to backend via `POST /login`.
  - **Error Handling:** Shows error message if authentication fails, clears on successful login.

#### `RegisterModal.js`

- **Description:** Registration modal for creating a new user account.
- **State Management:** Tracks `username`, `email`, `password`, and survey data.
- **Key Interactions:**
  - **User Creation:** Calls `POST /register` to create a new user account.
  - **Survey Data:** Optionally sends survey data to backend for profile personalization.

#### `ForgotPasswordModal.js`

- **Description:** Modal to initiate password reset process.
- **State Management:** Tracks `email` and displays messages for success or errors.
- **Key Interactions:**
  - **Password Reset:** Triggers `POST /forgotPassword` to send password reset email.

### Settings and Personalization Components

#### `NotificationPreferences.js`

- **Description:** Settings component allowing user to set notification preferences.
- **State Management:** Tracks toggles for each notification type.
- **Key Interactions:**
  - **Preference Update:** Sends updated preferences to backend via `POST /updatePreferences`.

#### `DarkModeToggle.js`

- **Description:** Toggle for dark mode.
- **State Management:** Tracks dark mode preference and saves to Redux.
- **Key Interactions:**
  - **UI Update:** Instantly applies dark mode styles when toggled.
  - **Preference Sync:** Saves setting to backend to persist across sessions.

---

## Backend Structure

### User Management

#### User Model (MongoDB Schema)

| **Attribute**         | **Type**      | **Description**                                                                           | **Example**   |
| --------------------- | ------------- | ----------------------------------------------------------------------------------------- | ------------- |
| `userID`              | String        | Unique identifier for each user.                                                          | `"user12345"` |
| `profileLevel`        | Integer (1-4) | User's current extremity level for content.                                               | `2`           |
| `engagementMetrics`   | Object        | Tracks user engagement, including streak count, notifications clicked, and articles read. | `{}`          |
| `personalizationData` | Object        | Stores demographics and preferences for personalized content.                             | `{}`          |

#### User Controller (`UserController.js`)

| **Method**                | **Description**                                             |
| ------------------------- | ----------------------------------------------------------- |
| `updateEngagementMetrics` | Updates `articlesRead` and `streakCount` in `User.js`.      |
| `adjustProfileLevel`      | Adjusts user’s `profileLevel` based on interaction history. |
| `getPersonalizationData`  | Retrieves personalization data for content recommendations. |

---

### Content Management

#### Article Model (MongoDB Schema)

| **Attribute**   | **Type**         | **Description**                                                   | **Example**             |
| --------------- | ---------------- | ----------------------------------------------------------------- | ----------------------- |
| `articleID`     | String           | Unique identifier for each article.                               | `"article98765"`        |
| `contentLevel`  | Enum (1-4)       | Degree of extremity, from factual to highly sensational content.  | `2`                     |
| `topicTags`     | Array of Strings | Tags categorizing the article, used for recommendation filtering. | `["health", "science"]` |
| `trendingScore` | Float            | Real-time relevance score based on trending data.                 | `8.7`                   |

#### Article Controller (`ArticleController.js`)

| **Method**             | **Description**                                  |
| ---------------------- | ------------------------------------------------ |
| `fetchArticlesByLevel` | Retrieves articles based on `profileLevel`.      |
| `updateTrendingScore`  | Updates `trendingScore` based on real-time data. |
| `insertHeroNarrative`  | Adds "hero narrative" to Level 4 articles.       |

---

### Profiling and Tailoring Algorithm

#### Algorithm Service (`ProfilingService.py`)

| **Attribute**         | **Type**         | **Description**                                                 | **Example**                |
| --------------------- | ---------------- | --------------------------------------------------------------- | -------------------------- |
| `userSentimentScore`  | Float            | Measures user sentiment based on article engagement.            | `0.85`                     |
| `engagementThreshold` | Float            | Sets threshold for profile level progression.                   | `0.5`                      |
| `behavioralHistory`   | Array of Objects | Stores user engagement history, including article interactions. | `[{ "articleID": "123" }]` |

#### Profiling Controller (`ProfilingController.py`)

| **Method**                | **Description**                                                            |
| ------------------------- | -------------------------------------------------------------------------- |
| `analyzeUserSentiment`    | Calculates `userSentimentScore` from interaction history.                  |
| `progressProfileLevel`    | Adjusts `profileLevel` based on sentiment and engagement patterns.         |
| `generateTailoredArticle` | Fetches and modifies articles based on `profileLevel` and trending topics. |

---

## Frontend-to-Backend Interactions

### Route Mappings and Data Flow

1. **HomePage.js**

   - **Frontend Components:** `TopHeadlinesSection.js`, `CurrentTopicsSection.js`
   - **Backend Routes:**
     - `GET /articles` -> Fetches articles based on `profileLevel`.

2. **UserProfile.js**

   - **Frontend Components:** `ProfileStreakCounter.js`, `EngagementStats.js`
   - **Backend Routes:**
     - `GET /personalData` -> Fetches user profile data.
     - `POST /updateMetrics` -> Updates streak and article count metrics.

3. **NotificationCenter.js**
   - **Frontend Components:** `NotificationItem.js`, `MarkAllAsReadButton.js`
   - **Backend Routes:**
     - `GET /notifications` to retrieve unread notifications.
     - `POST /markAllRead` to mark all notifications as read.

---
