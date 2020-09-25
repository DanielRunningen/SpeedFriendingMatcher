# SpeedFriendingMatcher

A quick script to process data gathered in Google Forms into match results that can be emailed to participants.

## Requirements

* Python 3.5 or higher
* `pip3` and `pipenv`

## Installation Instructions

1. Clone this repo with `git clone https://github.com/DanielRunningen/SpeedFriendingMatcher.git`.
2. Open the new directory and run `pipenv install`.
3. Run `pipenv shell` to open the new environment.
4. Make any changes to the `config.json` file, if needed (this includes paths to you input csv and desired output file).
5. Run `python3 match_maker.py config.json`

## `config.json` Setup

`config.json` holds all of the messy text, file paths, and regular expression patterns that might need to be changed on the fly if the input format changes or the desired output needs revision. Below is an example and an explaination for each key.

```json
{
    "csv_path" : "./data.csv",
    "output_path" : "./results.txt",
    "messages" : {
        "matched" : {
            "pre": "Congradulations, you have matches!",
            "post": "\n\n\n-----------------------\n\n\n\n"
        },
        "not_matched" : "Sorry, we didn't find any matches \n\n\n\n-----------------------\n\n\n\n"
    },
    "regex" : {
        "find_name" : ".*\\[([^\\]]+)\\]",
        "contact_methods" : "(email|facebook|discord|phone|meetup)"
    }
}
```

### `csv_path`

This should be the path to your input data. Please note that the input must be in a `.csv` format to work properly.

### `output_path`

This is the path the output will be placed in. There is no special formatting and all output will be pain text.

### `messages`

This section contains all of the plain text that should sorround the match results. There is logic to support two messages, one for participants who do find mutual matches, and another for individuals that find no matches.

#### `matched`

This hold two seperate texts, `pre` and `post`, that are used to print around the match results.

##### `pre`

A text string that prints before the match results are listed for each individual.

##### `post`

A text string that prints after the match results of each individual.

#### `not_matched`

Place text here to print out messages for individuals who did not recieve any matches.

#### `regex`

This section controls how information is gathered from the survey results.

##### `find_name`

This expressions should capture the name of a person in the column headers of the `.csv`. **Make sure that the name is contained in the first capture group so that it can be used in the comparisons.**

##### `contact_methods`

This expression is simply an `or` list of all the contact methods that a participant can give information for in your survey. **Please be sure to include at least `email` so the results can be printed correclty.**
