Run the full maintenance gate

please analyze the file llm-wiki-core-setup.md and do everything step by step according to the steps described there

 git -C "F:\____IL_AI\PCM" remote add origin https://github.com/ilpin301/CLEAR.git
 git -C "F:\____IL_AI\PCM" push -u origin master

------------------------------------------
The command is simply:
ingest any new files and run maintain. Don`t use grafify, only AGENTS.md
Ingest the new sources in Raw/Sources/
can you please ingest any new files and do not run maintain lint or query yet
can you please ingest any new files and run maintain lint or query yet
commit to git the changes

  That phrase triggers the llm-wiki-ingest skill. You can also say:

  - "Process the new Raw sources"
  - "Compile the three new PCM source files"

  All three will get me to read each new .md file in Raw/Sources/, extract key claims into focused Wiki notes (creating   or updating as needed), mark them Processed: true, and run the post-ingest maintenance gate (build, lint,
  source-scan, source-lint).

https://github.com/kepano/obsidian-skills

This project contains a folder with texts I've written named Mein_Schreibstil. Can you create a skill based on my texts for writing texts in my style in other projects without this folder ? Use the skill to convert PDFs to Markdown. The skill should only work when I ask you to create texts in German.
The skill should only work if I ask them to write in my style and only in German. It should also be able to work in synergy with other copyright skills if I specify them additionally.
