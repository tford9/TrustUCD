import pandas as pd
import cudf as cd


# Sample messages DataFrame
messages = cd.DataFrame({
    'id': [1, 2, 3, 4, 5],
    'parent_id': [None, 1, 2, 3, None],
    'content': [
        "Hello everyone!",
        "Hi! How are you?",
        "I'm doing well, thanks!",
        "Glad to hear that!",
        "Unrelated message"
    ]
})


def extract_threads(message_df, parent_id="parent_id", id="id", max_depth=10):
	threads = message_df.copy()
	depth = 0

	while depth < max_depth:
		# Merge messages onto threads where parent_id matches message id
		threads = threads.merge(
			message_df[['id', 'content']],
			left_on='parent_id',
			right_on='id',
			how='left',
			suffixes=('', f'_parent_{depth}')
		)
		
		# Rename the newly joined parent content column for clarity
		threads.rename(columns={f'content_parent_{depth}': f'content_{depth}'}, inplace=True)
		
		# If all parent_ids are now null, we're done
		if threads['parent_id'].isnull().all():
			break
	
		# Update parent_id to the next level's parent for the next merge
		threads['parent_id'] = threads[f'id_parent_{depth}']
		
		# Drop extra id column from the parent
		threads.drop(columns=[f'id_parent_{depth}'], inplace=True)
		
		depth += 1
		
	threads = threads.to_pandas()

		# Get all content columns in reverse order (root to current)
	content_cols = [f'content_{i}' for i in reversed(range(depth))] + ['content']
	
	# Build full thread text
	threads['full_thread'] = threads[content_cols].apply(
	    lambda row: ' -> '.join(filter(pd.notnull, row)),
	    axis=1
	)
	
	return threads

result = extract_threads(messages)

print(result[['id', 'full_thread']])