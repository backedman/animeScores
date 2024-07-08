# Anime Scorer/Tracker

Anime Tracker is a Python-based application that helps you manage and analyze your anime watching experience. It integrates with AniList to keep track of your anime list, provides recommendations, and offers detailed analytics on your watching habits.

## Installation

1. Download the latest release from the GitHub repository.
2. If you prefer to run the Python script directly:
   - Ensure you have Python 3.7+ installed
   - Install the required dependencies:
     ```
     pip install -r requirements.txt
     ```
3. Alternatively, you can use the provided .exe file for a standalone application.

## Usage

### Running the Application

- If using the Python script:
  ```
  python main.py
  ```
- If using the .exe file, simply double-click to run.

### Main Menu

When you start the application, you'll see a main menu with options:

```
1. Manual/New
2. Previous Page
3. Next Page
4. Choose Page
5. Search
6. Calculate Recommendations
7. Options
8. Exit Program
```

Use the corresponding numbers to navigate through the menu.

### Features

#### 1. Adding a New Anime

Select "Manual/New" from the main menu:

```
Name of anime?
> [Enter anime name]
```

#### 2. Recording Watching Stats

After selecting an anime:

```
1. Record Watching Stats
2. Get Watching Stats and Ratings
3. Other Settings
x. Go back
```

Choose "1" to record stats:

```
How do you rate Episode [X] of [Anime Name]?
> [Enter score]

Speed?
> [Enter speed if enabled]
```

#### 3. Viewing Stats

Choose "2" from the anime menu to view stats:

```
Average Score: [Score]
Scaled Score: [Score]
NN Score: [Score]
```

#### 4. Changing Anime Status

From the anime menu, choose "3" for Other Settings, then "1" to change status:

```
1. WATCHING
2. COMPLETED
3. PLANNING
4. DROPPED
5. PAUSED
```

#### 5. Setting Impact Score

In Other Settings, choose "2" to set the Impact Score:

```
Type impact score (1-10)
> [Enter score]
```

#### 6. Searching for Anime

From the main menu, choose "5" to search:

```
Name of anime to search
> [Enter search term]
```

#### 7. Getting Recommendations

From the main menu, choose "6" for recommendations. You can use various options:

```
r [options]

Options:
  -g, -genre="Genre"             Prioritize a genre
  -rg, -restrictgenre="Genre"    Deprioritize a genre
  -t, -tag="Tag"                 Prioritize a tag
  -rt, -restricttag="Tag"        Deprioritize a tag
  -list                          List all genres and tags
  -glist                         List all genres
  -tlist                         List all tags
  -type                          Use experimental neural network recommendations

Example:
r -g="Comedy,Adventure" -rt="Male Protagonist"
```

#### 8. Neural Network Score Prediction

The application uses a neural network to predict scores based on your watching habits. This happens automatically when you record stats.

## Configuration

You can modify the `config.txt` file to change settings like:

- Base watching speed
- Whether speed is changeable
- API Key

Example:
```txt
Enable_Speed_Changes: False
baseSpeed: 1.0
ANILIST UserID: <your user id is saved here>
ANILIST AuthToken: <auth token is saved here>
ANILIST AccessCode: <access token is saved here>
Preferred Score Saving(avg, scaled, real, nn): nn
```

## Syncing with AniList

The application automatically syncs with your AniList account. Make sure to set up your AniList API credentials (setup process happens first time process is run).

## Additional Notes

- The application calculates various scores:
  - Average Score: Simple average of episode ratings
  - Scaled Score: Adjusts for watching speed and episode count
  - NN Score: Prediction from the neural network
- The recommendation system uses your watching history and preferences to suggest new anime.
- You can track the speed at which you watch each episode, which factors into the scaled score.

Enjoy tracking and analyzing your anime watching experience with Anime Tracker!
