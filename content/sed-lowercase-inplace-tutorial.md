Title: Using sed to make specific text lower case in place
Date: 11-9-2014
Category: Tutorials
Tags: data, command line, sed

Data science, I'm sorry to say, often involves cleaning up input data into a usable and uniform format. Command line tools like grep, awk and sed provide an arcane power to manipulate text in files of arbitrary size. To continue on the arcane theme, mastering these tools can separate data science novices from data scientists with flaming robes. 

For the purposes of this tutorial we have a directory of files that among other lines have lines of the form: Tags: Tag1, Tag2, ... (zero or more Tag labels). Our goal is to convert the tag labels to lowercase (Tag1 -> tag1), but leave the rest of the file unchanged. You can download the example directory containing the files HERE LINK.

First we want to find all the files that contain the line we want to change. grep can do this, by searching all the files in the directory for lines that start with "Tags:"

    :::shell
    # -l : print only the file name
    # '^Tags:' : look for the string Tags: at the beginning of a line
    # *	: search all the files in the current directory
    grep -l "^Tags:" *

    # output:
    # tag-example1.txt
    # tag-example2.txt
    # tag-example3.txt

Even though the file called no-tag-example.txt contains the string "Tags:", that string is not at the start of line (that's what the ^ in ^Tags: specifies) so does not match our search.

Now we need to write a sed command to do the text manipulation to these files. The basic syntax for a sed substitution command is this:

    :::shell
    # s/ : do substitution
    # old/new : replace any occurances of "old" with "new"
    # /g : replace all found matches on the line, instead of only the first
    sed "s/old/new/g" filename

This command will not modify the file, it outputs the result to stdout (prints it to screen). Our goal is lower case everything after "Tags:", we'll go about constructing this command in steps. 

### Developing the command, step 1: Match the line. 

This sed command finds the lines containing "Tags:" and some other characters, and replaces the entire line with the string "changed".


    :::shell
    # the original file:
    cat tag-example1.txt

    # output:
    # Title: Tag example 1
    # Tags: Tag1, Tag2
    # 
    # Content

    # -r : use regular expressions
    # ^Tags:.+ : Search for "Tags" at the beginning of a line (^)
    #   followed by one or more other characters (.+).
    sed -r "s/^Tags:.+/changed/g" tag-example1.txt
    
    # output:
    # Title: Tag example 1
    # new
    # 
    # Content

### Developing the command, step 2: Lower case the line.

We don't want to replace the line with new text, we want to replace it with the old text in lower case (expect for the initial "Tag:" part). In a sed commend "\0" means "what was matched" and \L means "make lower case." Combining these we can lowercase the entire line.

    :::shell
    sed -r 's/^Tags:.+/\L\0/g' tag-example1.txt 

    # output:
    # Title: Tag example 1
    # tags: tag1, tag2
    # 
    # Content

### Developing the command, step 3: Lower case part of the line.

The problem with the above command is that is lower cases the entire line, including the initial "Tags:" part. To solve this problem we can enclose parts of our string to replace in parenthesis and access the first enclosed part as \1, the second as \2, ... in our replacement string. To lower case just the part after "Tags:":

    :::shell
    sed -r "s/(^Tags:)(.+)/\1\L\2/g" tag-example1.txt 

    # output:
    # Title: Tag example 1
    # Tags: tag1, tag2
    # 
    # Content

### Developing the command step 4: Feeding sed a list of files

