from pathos.multiprocessing import ProcessingPool as Pool
import os
import sys
import zstandard as zstd


def multi_proc(input_file):
	import json
	from tqdm import tqdm

	def read_whole_zst(file_name):
		# Create a Zstandard decompressor
		decompressor = zstd.ZstdDecompressor()

		# Read the compressed file into memory
		with open(file_name, "rb") as compressed_file:
			compressed_data = compressed_file.read()

		# Decompress the data
		decompressed_data = decompressor.decompress(compressed_data)

		# Convert the decompressed data to a string (assuming it contains text)
		text_data = decompressed_data.decode("utf-8")

		for _line in text_data.split('\n'):
			yield _line.strip()
		# return text_data

	_output_data = []

	for line, fh in tqdm(read_lines_zst(input_file[0])):
		obj = json.loads(line)
		# break
		if obj['subreddit'] in ["KingkillerChronicle", "PatrickRothfuss", "brandonsanderson", "Stormlight_Archive"]:
			_output_data.append(obj)
			# break
	# print(_output_data)
	# output = [obj.__dict__ for obj in _output_data]

	# Write list to JSON file
	fn = os.path.basename(input_file[0]).split('/')[-1]
	with open("/home/tford5/tmp/" + fn + "scraped.json", "w") as json_file:
		json.dump(_output_data, json_file, indent=4)

	return 0


def read_and_decode(reader, chunk_size, max_window_size, previous_chunk=None, bytes_read=0):
	chunk = reader.read(chunk_size)
	bytes_read += chunk_size
	if previous_chunk is not None:
		chunk = previous_chunk + chunk
	try:
		return chunk.decode()
	except UnicodeDecodeError:
		if bytes_read > max_window_size:
			raise UnicodeError(f"Unable to decode frame after reading {bytes_read:,} bytes")
		return read_and_decode(reader, chunk_size, max_window_size, chunk, bytes_read)


def read_lines_zst(file_name):
	with open(file_name, 'rb') as file_handle:
		buffer = ''
		reader = zstd.ZstdDecompressor(max_window_size=2**31).stream_reader(file_handle)
		while True:
			chunk = read_and_decode(reader, 2**27, 2**30)

			if not chunk:
				break
			lines = (buffer + chunk).split("\n")

			for line in lines[:-1]:
				yield line.strip(), file_handle.tell()

			buffer = lines[-1]

		reader.close()


input_folder = sys.argv[1]
input_files = []
for subdir, dirs, files in os.walk(input_folder):
	for filename in files:
		input_path = os.path.join(subdir, filename)
		if input_path.endswith(".zst"):
			if "2020" in input_path or "2021" in input_path or "2022" in input_path or "2023" in input_path:
				input_files.append([input_path])

# log.info(f"Processing {len(input_files)} files of {(total_size / (2**30)):.2f} gigabytes")
# output_file = open(sys.argv[2], "w")

print(input_files)

# Create a multiprocessing Pool
pool = Pool(processes=12)

# Map the file opening function to the file paths
pool.map(multi_proc, input_files)

# Close the pool
pool.close()
pool.join()
