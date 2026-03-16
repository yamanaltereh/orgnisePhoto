import datetime
import os
import logging
import re
import datetime
import shutil

# logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.DEBUG)

SOURCE_FOLDER_PATH = './data/SourcePhotos'
TARGET_FOLDER_PATH = './data/TargetPhotos'
OTHER_FOLDER_NAME = './data/others'
REJECTED_EXTENSIONS_FOLDER_NAME = './data/rejectedExtensions'

# def delete_file(file_name):
#   if os.path.exists(f'./images/{file_name}'):
#     os.remove(f'./images/{file_name}')
#   else:
#     print(f'The file with name {file_name} does not exist')

def convert_arabic_numerals(text):
  """Converts Eastern Arabic numerals in a string to Western Arabic numerals."""
  mapping = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')
  return text.translate(mapping)

def extractDate(file_name):
  try:
    # ex: 'IMG_20191021_172027.jpg' => '20191021'
    # ex: '20191021_172027.jpg' => '20191021'
    # ex: 'VID_20210523_102919.mp4' => '20210523'
    # ex: 'IMG_٢٠٢٢١٢٠١_٢٢٠٠٠٤.jpg' => '20221201'

    # Convert Arabic numerals to Western numerals
    normalized_file_name = convert_arabic_numerals(file_name)

    # Regex to find a date in YYYYMMDD format
    match = re.search(r'(20[0-2][0-9])(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[01])', normalized_file_name)
    if match:
      date_str = match.group(0)
      date = datetime.datetime.strptime(date_str, '%Y%m%d')
      if date.year > datetime.date.today().year:
        raise ValueError(f'Year {date.year} is in the future.')
      return date
    else:
      return '<Error>'
  except Exception as e:
    logging.error(f'Error: {e} - file_name: {file_name}')
    return '<Error>'

def scanFolder(basepath, prefix='.'):
  logger = logging.getLogger('scanFolder')
  res = []
  with os.scandir(basepath) as entries:
    for entry in entries:
      if entry.name.startswith('.'):
        continue
      if entry.is_dir():
        count = len([iq for iq in os.scandir(entry.path)])
        logger.debug(f'{prefix} Folder: {entry.name}, count: {count}')
        res += scanFolder(entry.path, prefix + '..')
      else:
        res += [entry]
        # info = entry.stat()
        logger.debug(f'{prefix} File: {entry.name}, Date: {extractDate(entry.name)}')
        # logger.debug(f'{prefix}.. Info: {info}')
  return res

def resetFile(file):
  os.rename(file.path, f'{SOURCE_FOLDER_PATH}/{file.name}')

def saveFile(file):
  date = extractDate(file.name)
  targetPath = TARGET_FOLDER_PATH
  file_name, file_extension = os.path.splitext(file.name)

  # Prepare the target path
  if (file_extension in rejectedExtensions):
    logging.debug(f'rejected extension with {file_name}, file_extension: {file_extension}')
    targetPath += REJECTED_EXTENSIONS_FOLDER_NAME
  elif (type(date) == datetime.datetime):
    targetPath += f'/{date.year}/{date.month}.{date.year}/{date.day}.{date.month}.{date.year}'
  else:
    targetPath += OTHER_FOLDER_NAME

  # Create directoy if not exist
  if not os.path.exists(targetPath):
    os.makedirs(targetPath)

  # os.copy(file.path, f'{targetPath}/{file.name}')
  shutil.copy2(file.path, f'{targetPath}/{file.name}', follow_symlinks=False)

def saveTargetFiles(files):
  logger = logging.getLogger('saveTargetFiles')
  logging.info('starting saving target ...')
  for file in files:
    saveFile(file)
  logging.info('Done saving target ...')

def resetTargetFiles():
  files = scanFolder(TARGET_FOLDER_PATH)
  for file in files:
    resetFile(file)

def print(files):
  for file in files:
    date = extractDate(file.name)
    if (type(date) == datetime.datetime):
      date_str = f'{date.year}/{date.month}/{date.day}'
    else:
      date_str = '<Error>'
    logging.debug(f'{file.name}, {date_str}')

rejectedExtensions = ['.json'];

def filterFiles(files):
  newFiles = []
  for file in files:
    file_name, file_extension = os.path.splitext(file.name)
    if (file_extension in rejectedExtensions):
      logging.debug(f'rejected extension with {file_name}, file_extension: {file_extension}')
    else:
      newFiles.append(file)

  return newFiles

def main():
  logger = logging.getLogger('main')
  logger.debug(f'Start {datetime.datetime.now()}')

  files = scanFolder(SOURCE_FOLDER_PATH)
  logging.debug(f'Files Count: {len(files)}')

  # print(files)

  # files = filterFiles(files)
  saveTargetFiles(files)

  # resetTargetFiles()

  logger.debug(f'Finish {datetime.datetime.now()}')

if __name__ == '__main__':
    main()
