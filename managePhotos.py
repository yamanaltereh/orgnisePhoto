import datetime
import os
import logging
import re
import datetime
import shutil

# logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.DEBUG)

print(f'Hello {datetime.datetime.now()}')

def delete_file(file_name):
  if os.path.exists(f'./images/{file_name}'):
    os.remove(f'./images/{file_name}')
  else:
    print(f'The file with name {file_name} does not exist')

def extractDate(file_name):
  # ex: 'IMG_20191021_172027.jpg' => '20191021'
  # ex: '20191021_172027.jpg' => '20191021'
  # match = re.search(r'[_|-]?(.*?)[_|-]', file_name)
  match = re.search(r'[2019|2020]([0-9]){7}', file_name)
  if match:
    return datetime.datetime.strptime(match.group(0), '%Y%m%d')
  else:
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
        # logger.debug(f'{prefix} Folder: {entry.name}, count: {count}')
        res += scanFolder(entry.path, prefix + '..')
      else:
        res += [entry]
        info = entry.stat()
        # logger.debug(f'{prefix} File: {entry.name}, Date: {extractDate(entry.name)}')
        # logger.debug(f'{prefix}.. Info: {info}')
  return res

def resetFile(file):
  sourcePath = './SourcePhotosTest'
  os.rename(file.path, f'{sourcePath}/{file.name}')

def saveFile(file):
  date = extractDate(file.name)
  basepath = './TargetPhotosTest'
  targetPath = basepath

  # Prepare the target path
  if (type(date) == datetime.datetime):
    targetPath += f'/{date.year}/{date.year}.{date.month}/{date.year}.{date.month}.{date.day}'
  else:
    targetPath += '/others'

  # Create directoy if not exist
  if not os.path.exists(targetPath):
    os.makedirs(targetPath)

  os.rename(file.path, f'{targetPath}/{file.name}')

def saveTargetFiles(files):
  logger = logging.getLogger('saveTargetFiles')
  logging.info('starting saving target ...')
  for file in files:
    saveFile(file)

def resetTargetFiles():
  basepath = './TargetPhotosTest'
  files = scanFolder(basepath)
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

def main():
  logger = logging.getLogger('main')
  logging.info('started main ...')
  
  # List all subdirectories using scandir()
  basepath = './SourcePhotosTest'
  files = scanFolder(basepath)
  logging.debug(f'Files Count: {len(files)}')

  print(files)

  saveTargetFiles(files)

  # resetTargetFiles()

if __name__ == '__main__':
    main()
