Title: Using sed to make specific text lower case in place
Date: 11-9-2014
Category: Tutorials
Tags: data, command line, sed

Data science, I'm sorry to say, often involves cleaning up input data into a usable and uniform format. Command line tools like `grep`, `awk` and `sed` provide an arcane power to manipulate text in files of arbitrary size. To continue on the arcane theme, mastering these tools can separate data science novices from data scientists with flaming robes. 

For the purposes of this tutorial we have a directory of files that have some lines of the form: Tags: Tag1, Tag2, ... (zero or more Tag labels). Our goal is to convert the tag labels to lowercase (Tag1 -> tag1), but leave the rest of the file unchanged. You can download the example directory containing the files HERE LINK.

## The answer

    :::console
    $ git grep -lz "^Tags:" | xargs -0 sed -i -r "s/(^Tags:)(.+)/\1\L\2/g"

## Explanation

The [`sed`](http://www.grymoire.com/Unix/Sed.html#uh-0) command allows for substitution of strings in text. We'll use a `sed` command to do the text manipulation (lower casing of tag names) on these files. The basic syntax for a `sed` substitution command is this:

    :::console
    $ # s/ : do substitution
    $ # old/new : replace any occurrences of "old" with "new"
    $ # /g : replace all found matches on the line, instead of only the first
    $ # filename : the name of the file to search and replace text in
    $ sed "s/old/new/g" filename

This command will not modify the file, it outputs the result to stdout (prints it to screen). Our goal to construct a `sed` command to lower case everything after "Tags:", modifying the file in place and not changing any files that aren't under version control. We'll go about constructing this command in steps. 

### Developing the command, step 1: Match the line. 

This `sed` command finds the lines containing "Tags:" and any other characters, and replaces the entire line with the string "changed".


    :::console
    $ # the original file:
    $ cat tag-example1.txt
    Title: Tag example 1
    Tags: Tag1, Tag2
     
    Content
    $ # -r : use regular expressions
    $ # ^Tags:.+ : Search for "Tags" at the beginning of a line (^)
    $ #   followed by one or more other characters (.+).
    $ sed -r "s/^Tags:.+/new/g" tag-example1.txt
    Title: Tag example 1
    new
     
    Content

### Developing the command, step 2: Lower case the line.

We don't want to replace the line with new text, we want to replace it with the old text in lower case (expect for the initial "Tag:" part). In a `sed` command `\0` means "what was matched" and `\L` means "make lower case." Combining these we can lowercase the entire line.

    :::console
    $ sed -r "s/^Tags:.+/\L\0/g" tag-example1.txt 
    Title: Tag example 1
    tags: tag1, tag2
     
    Content

### Developing the command, step 3: Lower case part of the line.

The problem with the above command is that it lower cases the entire line, including the initial "Tags:" part. To solve this problem we can enclose parts of our string to replace in parenthesis and access the first enclosed part as `\1`, the second as `\2`, ... in our replacement string. To lower case just the part after "Tags:":

    :::console
    $ sed -r "s/(^Tags:)(.+)/\1\L\2/g" tag-example1.txt 
    Title: Tag example 1
    Tags: tag1, tag2
     
    Content

### Developing the command step 4: Finding the files to change

Now its time to replace the text of the actual files with the `-i` flag (`-i ''` on Mac OSX). This operation could be dangerous if the files are not under version control, so we'll use git to find and change only files in the git repo.

    :::console
    $ # outputs the file name and the matching line
    $ git grep "^Tags:"
    tag-example1.txt:Tags: tag1, tag2
    tag-example2.txt:Tags: tag1
    tag-example3.txt:Tags: tag1, tag2, tag3
    $ # outputs just the file names
    $ git grep -l "^Tags:"
    tag-example1.txt
    tag-example2.txt
    tag-example3.txt
    $ # outputs the file names separated by a null character
    $ git grep -lz "^Tags:"
    tag-example1.txt^@tag-example2.txt^@tag-example3.txt^@

### Developing the command step 5: The complete command

We can use the `xargs` tool to tell `sed` to act on the list of files we found in step 4.

    :::console
    $ # outputs the files to be changed
    $ git grep -lz "^Tags:" | xargs -0 echo
    tag-example1.txt tag-example2.txt tag-example3.txt
    $ # changes the files:
    $ git grep -lz "^Tags:" | xargs -0 sed -i -r "s/(^Tags:)(.+)/\1\L\2/g"

### Developing the command step 6: Inspect the results with `git diff`

We can confirm that we got the correct outcome with `git diff`

    :::console
    $ git diff
    diff --git a/tag-example1.txt b/tag-example1.txt
    index 589bbdf..7d57a7d 100644
    --- a/tag-example1.txt
    +++ b/tag-example1.txt
    @@ -1,4 +1,4 @@
     Title: Tag example 1
    -Tags: Tag1, Tag2
    +Tags: tag1, tag2
     
     Content
    diff --git a/tag-example2.txt b/tag-example2.txt
    index addcd3b..d271212 100644
    --- a/tag-example2.txt
    +++ b/tag-example2.txt
    @@ -1,4 +1,4 @@
     Title: Tag example 2
    -Tags: Tag1
    +Tags: tag1
     
     Content
    diff --git a/tag-example3.txt b/tag-example3.txt
    index c8b10e1..42e0a75 100644
    --- a/tag-example3.txt
    +++ b/tag-example3.txt
    @@ -1,4 +1,4 @@
     Title: Tag example 3
    -Tags: Tag1, Tag2, Tag3
    +Tags: tag1, tag2, tag3
