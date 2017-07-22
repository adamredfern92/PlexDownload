import os
import plexapi
from multiprocessing import Process
import progressbar
from plexapi.server import PlexServer
from PlexConfig import *
from Functions import newFolder

def newFolder(path):
    try:
        os.makedirs(path)
    except OSError as exc:  
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def downloadSelection(selection, savePath, fileName):
	if not os.path.exists(os.path.join(savePath,fileName)):
		newFolder(savePath)
		print 'Downloading {}'.format(fileName.encode('utf-8'))
		fileSize = selection.media[0].parts[0].size
		downloadProcess = Process(target=selection.download, kwargs={'savepath':savePath, 'keep_orginal_name':True})
		downloadProcess.start()
		currentSize = 0
		with progressbar.ProgressBar(max_value=fileSize) as bar:
			while downloadProcess.is_alive():
				if os.path.exists(os.path.join(savePath,fileName)):
					currentSize = os.path.getsize(os.path.join(savePath,fileName))
					if currentSize > 0:
						bar.update(currentSize)

def downloadEpisode(selection):
	show = selection.show().title 
	season = selection.season().title
	episodeFolder = os.path.join(show, season)
	savePath = os.path.join(tvShowLibrary, episodeFolder)
	fileName = selection.media[0].parts[0].file.split('/')[-1]
	downloadSelection(selection, savePath, fileName)

def downloadMovie(selection):
	movieFolder = '{} ({})'.format(selection.title, selection.year)
	savePath = os.path.join(movieLibrary, movieFolder)
	fileName = selection.media[0].parts[0].file.split('/')[-1]
	downloadSelection(selection, savePath, fileName)

tvShowLibrary = os.path.join(libraryPath,'TV Shows')
movieLibrary = os.path.join(libraryPath,'Movies')

newFolder(tvShowLibrary)
newFolder(movieLibrary)

plex = PlexServer(plexUrl, plexToken)

home = True

print ''

while home:
	os.system('clear')
	print ''
	searchTerm = raw_input('Search for item(s) to download: ')

	if searchTerm.lower() == 'exit':
		home = False
		continue
	elif searchTerm.lower() == 'ondeck':
		onDeckItems = plex.library.onDeck()[:10]
		for onDeckItem in onDeckItems:
			if onDeckItem.TYPE=='episode':
				downloadEpisode(onDeckItem)
			elif onDeckItem.TYPE=='movie':
				downloadMovie(onDeckItem)
		raw_input('Done! Press enter to continue...')
		continue


	print 'Searching...'
	print ''

	searchList = plex.search(searchTerm)


	if len(searchList) == 0:
		print 'No items found'
		continue

	actualSearchList = []
	for item in searchList:
		if isinstance(item, plexapi.video.Show) or isinstance(item, plexapi.video.Movie) or isinstance(item, plexapi.video.Episode):
			actualSearchList.append(item)
			

	searching = True

	while searching:
		os.system('clear')
		print ''
		print 'Searching for \'{}\''.format(searchTerm)
		print ''
		num = 1
		for item in actualSearchList:
			if item.TYPE == 'episode':
				print '{: 2}. {: <7} - {} - S{:02}E{:02} - {}'.format(
						num, item.TYPE.capitalize(), item.show().title.encode('utf-8'), item.season().index, item.index, item.title.encode('utf-8')
					)
			else:
				print '{: 2}. {: <7} - {}'.format(num, item.TYPE.capitalize(), item.title.encode('utf-8'))
			num += 1

		print ''	
		searchItem = raw_input('Select Item: ')

		if searchItem.lower() == 'back':
			searching = False
			continue
		elif searchItem.lower() == 'exit':
			searching = False
			home = False
			continue
		else:
			try:
				searchIndex = int(searchItem)
			except:
				print 'Must be int from list'
				print ''
				continue

		if searchIndex <= 0 or searchIndex > len(actualSearchList):
			print 'Must be int form list'
			print ''
			continue
		else:
			selection = actualSearchList[searchIndex-1]

		print ''

		if isinstance(selection, plexapi.video.Movie):
			downloadMovie(selection)
			raw_input('Done! Press enter to continue...')
			searching=False
		elif isinstance(selection, plexapi.video.Episode):
			downloadEpisode(selection)
			raw_input('Done! Press enter to continue...')
			searching=False
		elif isinstance(selection, plexapi.video.Show):
			seasonSearch = True
			while seasonSearch:
				os.system('clear')
				print ''
				print '{}'.format(selection.title)
				print ''
				for seasonInSelection in selection.seasons():
					print seasonInSelection.title
				print ''
				seasonNo = raw_input('Select Season Number (or all/unwatched): ')
				print ''


				if seasonNo.lower() == 'back':
					seasonSearch = False
					continue
				elif seasonNo.lower() == 'exit':
					seasonSearch = False
					searching = False
					home = False
					continue
				elif seasonNo.lower() == 'all':
					for seasonDownload in selection.seasons():
						for episodeDownload in seasonDownload.episodes():
							downloadEpisode(episodeDownload)
					raw_input('Done! Press enter to continue...')
					seasonSearch = False
					searching = False
					continue
				elif seasonNo.lower() == 'unwatched':
					for seasonDownload in selection.seasons():
						for episodeDownload in seasonDownload.episodes():
							if not episodeDownload.isWatched:
								downloadEpisode(episodeDownload)
					raw_input('Done! Press enter to continue...')
					seasonSearch = False
					searching = False
					continue
				else:
					try:
						seasonIndex = int(seasonNo)
					except:
						print 'Must be season number or all/unwatched'
						print ''
						continue

				if seasonIndex <= 0 or seasonIndex > len(selection.seasons()):
					print 'Must be season number or all/unwatched'
					print ''
					continue
				else:
					seasonSelection = selection.seasons()[seasonIndex-1]
					episodeSearch = True
					while episodeSearch:
						os.system('clear')
						print ''
						print '{} - {}'.format(selection.title.encode('utf-8'), seasonSelection.title.encode('utf-8'))
						print ''
						for episodeInSelection in seasonSelection.episodes():
							print '{} - {}'.format(episodeInSelection.index, episodeInSelection.title.encode('utf-8'))
						print ''
						episodeNo = raw_input('Select Episode Number (or all/unwatched): ')
						print ''


						if episodeNo.lower() == 'back':
							episodeSearch = False
							continue
						elif episodeNo.lower() == 'exit':
							episodeSearch = False
							seasonSearch = False
							searching = False
							home = False
							continue
						elif episodeNo.lower() == 'all':
							for episodeDownload in seasonSelection.episodes():
								downloadEpisode(episodeDownload)
							raw_input('Done! Press enter to continue...')
							episodeSearch = False
							seasonSearch = False
							searching = False
							continue
						elif episodeNo.lower() == 'unwatched':
							for episodeDownload in seasonSelection.episodes():
								if not episodeDownload.isWatched:
									downloadEpisode(episodeDownload)
							raw_input('Done! Press enter to continue...')
							episodeSearch = False
							seasonSearch = False
							searching = False
							continue
						else:
							try:
								episodeIndex = int(episodeNo)
							except:
								print 'Must be episodes number or all/unwatched'
								print ''
								continue

						if episodeIndex <= 0 or episodeIndex > len(seasonSelection.episodes()):
							print 'Must be season number or all/unwatched'
							print ''
							continue
						else:
							episodeSelection = seasonSelection.episodes()[episodeIndex-1]
							downloadEpisode(episodeSelection)
							raw_input('Done! Press enter to continue...')
							episodeSearch = False
							seasonSearch = False
							searching = False
							continue

		print ''



