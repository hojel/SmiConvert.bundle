# 1. goto 2 if SMI file exists else end
# 2. goto 4 if encoding of SMI is Unknown
# 3. convert Unicode to CP949
# 4. goto 5 check both [KR|EN]CC keywords exists
# 5. divide SMI files

import os
from smi_demux import demuxSMI
from smi2srt import convertSMI

def Start():
  pass

def convertSubtitles(part, SaveSRT):
  Log(part.file)
  basePath = os.path.splitext(part.file)[0]
  smiPath = basePath+'.smi'
  if not os.path.exists(smiPath):
    Log('%s not found!', smiPath)
    return False

  ext = '.smi'

  # (1) transcode to CP949
  subData = Core.storage.load(smiPath)
  subEncoding = chdet(subData)
  if subEncoding != 'Unknown':
    Log('%s transcode to cp949', subEncoding)
    subData = unicode(subData, subEncoding, 'ignore').encode('cp949', 'ignore')

  # (2) split languages if needed
  result = demuxSMI(subData)

  # (3) convert SMI to SRT
  if SaveSRT:
    result2 = dict()
    for lang, smiData in result.iteritems():
      result2[lang] = convertSMI(smiData.decode('cp949','ignore').encode('utf-8'))
      Log('convert(%s): %d -> %d' % (lang, len(smiData), len(result2[lang])))
    result = result2
    ext = '.srt'

  # (4) save
  if not SaveSRT and subEncoding == 'Unknown':
    return True  # no need to save
  if len(result) > 1:
    for lang, subData in result.iteritems():
      Core.storage.save(basePath+'.'+lang+ext, subData)
  elif SaveSRT or subEncoding != 'Unknown':
    Core.storage.save(basePath+'.ko'+ext, result['unknown'])
  return True

def chdet(aBuf):
    # If the data starts with BOM, we know it is UTF
  if aBuf[:3] == '\xEF\xBB\xBF':
    # EF BB BF  UTF-8 with BOM
    result = "UTF-8"
  elif aBuf[:4] == '\xFF\xFE\x00\x00':
    # FF FE 00 00  UTF-32, little-endian BOM
    result = "UTF-32LE"
  elif aBuf[:4] == '\x00\x00\xFE\xFF': 
    # 00 00 FE FF  UTF-32, big-endian BOM
    result = "UTF-32BE"
  elif aBuf[:4] == '\xFE\xFF\x00\x00':
    # FE FF 00 00  UCS-4, unusual octet order BOM (3412)
    result = "X-ISO-10646-UCS-4-3412"
  elif aBuf[:4] == '\x00\x00\xFF\xFE':
    # 00 00 FF FE  UCS-4, unusual octet order BOM (2143)
    result = "X-ISO-10646-UCS-4-2143"
  elif aBuf[:2] == '\xFF\xFE':
    # FF FE  UTF-16, little endian BOM
    result = "UTF-16LE"
  elif aBuf[:2] == '\xFE\xFF':
    # FE FF  UTF-16, big endian BOM
    result = "UTF-16BE"
  else:
    result = "Unknown"
  return result

# entry for Movie
class SmiSubtitleAgentMovies(Agent.Movies):
  name = 'SMI Converter'
  #languages = [Locale.Language.NoLanguage]
  languages = [Locale.Language.Korean]
  primary_provider = False
  
  def search(self, results, media, lang):
    results.Append(MetadataSearchResult(id = 'null', score = 100))
    
  def update(self, metadata, media, lang):
    SaveSRT = Prefs['save_srt']
    for i in media.items:
      for part in i.parts:
        convertSubtitles(part, SaveSRT)

# entry for TV shows
class SmiSubtitleAgentTV(Agent.TV_Shows):
  name = 'SMI Converter'
  #languages = [Locale.Language.NoLanguage]
  languages = [Locale.Language.Korean]
  primary_provider = False

  def search(self, results, media, lang):
    results.Append(MetadataSearchResult(id = 'null', score = 100))

  def update(self, metadata, media, lang):
    SaveSRT = Prefs['save_srt']
    for s in media.seasons:
      # just like in the Local Media Agent, if we have a date-based season skip for now.
      if int(s) < 1900:
        for e in media.seasons[s].episodes:
          for i in media.seasons[s].episodes[e].items:
            for part in i.parts:
              convertSubtitles(part, SaveSRT)
