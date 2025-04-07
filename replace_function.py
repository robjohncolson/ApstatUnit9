def replace_function_in_file(filename, function_name, replacement_code):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Find the starting line of the function
        start_line = -1
        for i, line in enumerate(lines):
            if f"function {function_name}" in line:
                start_line = i
                break
        
        if start_line == -1:
            return f"Function '{function_name}' not found in the file"
        
        # Find the end of the function (looking for closing brace)
        end_line = start_line
        brace_count = 0
        found_opening_brace = False
        
        for i in range(start_line, len(lines)):
            line = lines[i]
            
            # Count opening braces
            if "{" in line:
                found_opening_brace = True
                brace_count += line.count("{")
            
            # Count closing braces
            if "}" in line:
                brace_count -= line.count("}")
            
            # When brace count is 0 and we've found at least one opening brace, we've reached the end
            if found_opening_brace and brace_count == 0:
                end_line = i
                break
        
        # Print information about the found function
        original_function = ''.join(lines[start_line:end_line+1])
        function_length = end_line - start_line + 1
        print(f"Found '{function_name}' from line {start_line+1} to {end_line+1} ({function_length} lines)")
        
        # Replace the function with the new code
        lines[start_line:end_line+1] = [replacement_code + "\n"]
        
        # Write the modified content back to the file
        with open(filename, 'w', encoding='utf-8') as file:
            file.writelines(lines)
            
        return f"Successfully replaced function '{function_name}' in {filename}"
            
    except FileNotFoundError:
        return f"Error: File '{filename}' not found"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    filename = "index.html"
    function_name = "markTopicAsCompleted"
    
    replacement_code = """        // Function to mark all videos and quizzes in a topic as completed
        function markTopicAsCompleted(topicId) {
            const topic = pdfFiles.find(t => t.id === topicId);
            if (!topic) return;

            console.log(`DEBUG (markTopic): Marking topic ${topicId} as completed.`);

            // --- NEW: Track items to save to Supabase ---
            const itemsToSave = [];

            // Mark all videos as completed and queue for saving
            topic.videos.forEach(video => {
                // Only mark/save if not already completed
                if (!video.completed) {
                    video.completed = true;
                    video.completionDate = video.completionDate || new Date().toISOString();
                    const videoIdentifier = video.url || video.altUrl;
                    if (videoIdentifier) {
                        itemsToSave.push({ type: 'video', identifier: videoIdentifier });
                        console.log(`DEBUG (markTopic): Queued video ${videoIdentifier} for saving.`);
                    } else {
                         console.warn(`DEBUG (markTopic): Skipping video in topic ${topicId} due to missing identifier.`);
                    }
                }
            });

            // Mark all quizzes as completed and queue for saving
            topic.quizzes.forEach(quiz => {
                 // Only mark/save if not already completed
                if (!quiz.completed) {
                    quiz.completed = true;
                    quiz.completionDate = quiz.completionDate || new Date().toISOString();
                    itemsToSave.push({ type: 'quiz', identifier: quiz.quizId });
                    console.log(`DEBUG (markTopic): Queued quiz ${quiz.quizId} for saving.`);
                }
            });

            topic.current = false;

            // Automatically mark the next topic as current
            const currentIndex = pdfFiles.findIndex(t => t.id === topicId);
            if (currentIndex >= 0 && currentIndex < pdfFiles.length - 1) {
                const nextTopic = pdfFiles[currentIndex + 1];
                if (nextTopic) {
                    nextTopic.current = true;
                }
            }

            // Update local storage FIRST to persist completion status locally
            saveTopicProgress();
             console.log(`DEBUG (markTopic): Local progress saved for topic ${topicId}.`);

            // --- NEW: Save queued items to Supabase ---
            if (currentUserId && itemsToSave.length > 0) {
                 console.log(`DEBUG (markTopic): Attempting to save ${itemsToSave.length} items to Supabase for user ${currentUserId}.`);
                // Use Promise.allSettled to attempt all saves even if some fail
                Promise.allSettled(itemsToSave.map(item =>
                    saveCompletionToSupabase(item.type, item.identifier, UNIT_ID)
                )).then(results => {
                    // Log results (optional)
                    results.forEach((result, index) => {
                        const item = itemsToSave[index];
                        if (result.status === 'fulfilled') {
                            console.log(`DEBUG (markTopic): Successfully saved ${item.type} ${item.identifier} to Supabase.`);
                        } else {
                            console.error(`DEBUG (markTopic): Failed to save ${item.type} ${item.identifier} to Supabase:`, result.reason);
                        }
                    });
                     // Check quota AFTER attempting Supabase saves
                     console.log(`DEBUG (markTopic): Triggering quota check after Supabase saves.`);
                     checkDailyQuotaCompletion();
                });
            } else if (itemsToSave.length > 0) {
                // If no user ID, we rely on the local storage update and potential future sync
                console.warn(`DEBUG (markTopic): No user ID or no items needed saving to Supabase. Local state updated.`);
                // Check local quota based on local state change if needed (though checkDailyQuotaCompletion primarily uses Supabase now)
                // checkDailyQuotaCompletion(); // Maybe call this anyway if you want local visual updates? It might double-trigger if Supabase succeeds later.
                 console.log(`DEBUG (markTopic): Triggering quota check even without Supabase saves (may rely on local logic if implemented).`);
                 checkDailyQuotaCompletion(); // Call it regardless to update visuals based on fetched data
            } else {
                 console.log(`DEBUG (markTopic): No new items were marked complete.`);
                 // Check quota anyway, in case this function is called when topic already complete
                 console.log(`DEBUG (markTopic): Triggering quota check (topic might have been already complete).`);
                 checkDailyQuotaCompletion();
            }


            // Refresh the UI immediately based on local changes
            populateTopicCards();
            updateCurrentTopicInfo();
            populateQuickAccessTopics();
            updateProgressBar();

            // Scroll to next topic in study materials tab if applicable
            if (currentIndex >= 0 && currentIndex < pdfFiles.length - 1 && document.getElementById('content-study-materials').classList.contains('active')) {
                const nextCard = document.getElementById(`topic-card-${pdfFiles[currentIndex + 1]?.id}`);
                if (nextCard) {
                    setTimeout(() => {
                        nextCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }, 100); // Small delay allows UI to update first
                }
            }
        }"""
    
    result = replace_function_in_file(filename, function_name, replacement_code)
    print(result) 