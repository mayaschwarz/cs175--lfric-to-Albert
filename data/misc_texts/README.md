# Collection of Miscellanous Translated Texts

Collection of texts in Old and Middle English texts that have been successfully translated in Modern English.

### Key Table
The master table containing all metadata information about each 
text is stored as an entry in `t_key.csv` following the format:

```id, table, abbreviation, language, title, info_text, info_url, publisher, copyright, copyright_info```

* `id` - id given to each unique text
* `table` - filename of the text's csv
* `abbreviation` - shorthand (acronym_author initials)
* `language` - middle english or old english
* `title` - title of the text
* `info_text` - short description of the text
* `info_url` - url of description
* `publisher` - publisher
* `copyright` - copyright of text
* `copyright_info` - additional copyright information

### Text Table
Each text is broken into entries of matching sentences with each row format as:

```id, text, translation```
* `id` - sentence id
* `text` - original text
* `translation` - modern english translation