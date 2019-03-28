#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This work was created by participants in the DataONE project, and is
# jointly copyrighted by participating institutions in DataONE. For
# more information on DataONE, see our web site at http://dataone.org.
#
#   Copyright 2009-2016 DataONE
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Random words.

A selection of 1000 words pulled randomly from /usr/share/dict/words using the
randomWords method below.

"""

import codecs
import random

# Yapf gets into some kind of worst case performance when formatting this,
# so we disable it.
# yapf: disable
WORDS_1K = [
  'untrimmed', 'Hydriote', 'burnish', 'tsia', 'petiolary', 'vocative',
  'incensement', 'periodic', 'Klikitat', 'stipendiarian', 'witchwood',
  'congressionally', 'caftaned', 'heartsease', 'mezcal', 'ostensibility',
  'caudotibialis', 'adenopharyngeal', 'cyanophoric', 'unattempting',
  'seawoman', 'interlaced', 'outquaff', 'topgallant', 'Mesohippus',
  'geraniaceous', 'Gelechia', 'autothermy', 'dowie', 'Sorbus', 'fortlet',
  'inferiorism', 'cystopyelitis', 'slart', 'bestench', 'Odontaspidae',
  'cautioner', 'stowbordman', 'amphivasal', 'heroicity', 'unpatronizable',
  'cockhorse', 'purtenance', 'indocible', 'untimedness', 'viscus',
  'reinvolve', 'celiectomy', 'outcut', 'unsupped', 'nonamputation',
  'syphilogenesis', 'seaplane', 'courtezanry', 'Coregonus', 'middlewards',
  'submeningeal', 'unmethodicalness', 'duraplasty', 'aflagellar',
  'semicriminal', 'caudally', 'mycetism', 'profiteering', 'nephridium',
  'subobscure', 'unjointured', 'magnetostriction', 'membranocartilaginous',
  'iteming', 'bestiality', 'illuminating', 'restoration', 'multisect',
  'bellows', 'thalassinid', 'midweekly', 'typhloenteritis', 'Castilloa',
  'betail', 'synoeciously', 'receiptor', 'syntypicism', 'gunyeh',
  'sluggishly', 'landwhin', 'plaud', 'scrutinizingly', 'twanginess',
  'diphyodont', 'sibship', 'sisham', 'stradine', 'geotechnic',
  'recompetitor', 'tieback', 'coracoid', 'trapezohedron', 'beclog',
  'diathermy', 'recrementitial', 'thaumaturgic', 'malengine', 'advanced',
  'musicographer', 'algraphic', 'Rhinosporidium', 'absinthian', 'reman',
  'dispositively', 'innocency', 'irresistance', 'lumbricoid',
  'portulacaceous', 'fruitwise', 'kilostere', 'ascogonium', 'laughful',
  'monoliteral', 'polytonic', 'ramfeezled', 'idiotry', 'subterrene',
  'weakishness', 'lockbox', 'apronful', 'Dike', 'regrating',
  'Hispaniolize', 'scazontic', 'Cyclosporeae', 'yez', 'Phylloceratidae',
  'grangerite', 'brightsmith', 'amorphic', 'eudaemonical', 'butanolide',
  'monetary', 'omental', 'macrostylospore', 'lam', 'Buddha', 'immerd',
  'breediness', 'osmetic', 'ampyx', 'transaccidentation', 'fluoridation',
  'domatophobia', 'sculpt', 'futural', 'auxanology', 'chalcographic',
  'Anglophobiac', 'dealership', 'catelectrotonus', 'outfable',
  'revealability', 'efflorescence', 'proczarist', 'forebody', 'unsteck',
  'Darrell', 'blastid', 'piation', 'beetle', 'Batrachospermum',
  'additionist', 'descriptionless', 'Alliaceae', 'carbanil', 'unboat',
  'demifigure', 'amy', 'Anne', 'cereous', 'Platystomidae', 'antistrophic',
  'daughterhood', 'probuilding', 'unrealizable', 'nonabstemious',
  'tattlery', 'bicrescentic', 'arcking', 'tai', 'somepart',
  'Potamochoerus', 'crookbacked', 'picturer', 'Smintheus', 'beauism',
  'uprear', 'uncorseted', 'housebreaker', 'overconservatively',
  'cerussite', 'Triangula', 'pesthouse', 'stoppableness', 'nebularization',
  'escalloniaceous', 'helminthological', 'nondisinterested', 'popish',
  'enlard', 'creosol', 'untransported', 'intermaxillar', 'incessable',
  'enterolithiasis', 'semisacerdotal', 'unpointed', 'Deuterostomata',
  'marbler', 'quaternate', 'willer', 'puddening', 'rapiner', 'bisexed',
  'idolatrousness', 'undarkened', 'handicraftsmanship', 'oystered',
  'stromateoid', 'thermostable', 'multiseated', 'panclastic', 'fifie',
  'unnullified', 'sanguinivorous', 'hellborn', 'hypermetamorphic',
  'telemetrical', 'V', 'continuando', 'phenoplast', 'invection',
  'ostreiculturist', 'swaler', 'irritableness', 'impingence', 'Liparian',
  'dosimetric', 'unplanned', 'Johannine', 'alkalinuria', 'semipenniform',
  'goldbug', 'ameliorativ', 'ratwood', 'employless', 'unsusceptibility',
  'multilaminar', 'burrito', 'psoriatic', 'kele', 'enterprising', 'begob',
  'chaplain', 'hosting', 'nundine', 'spectroelectric', 'extracapsular',
  'Alcicornium', 'westering', 'droop', 'deferrization', 'columbotitanate',
  'hyperacid', 'enantiomorphism', 'flexured', 'sangreeroot', 'seizure',
  'saumon', 'Ismaelitish', 'glyconin', 'brekkle', 'acotyledonous',
  'crispness', 'upcrop', 'spermatangium', 'Melinae', 'cateran',
  'momentariness', 'paintingness', 'radiometry', 'ballooner', 'arthropod',
  'mincemeat', 'thyroidean', 'asterion', 'poetastry', 'penetrology',
  'querimoniousness', 'hypha', 'strident', 'unclouded', 'obfuscous',
  'regulatorship', 'scaffold', 'acclinal', 'isochroous', 'glossoid',
  'infecter', 'venenation', 'antennal', 'funds', 'cantoon', 'chrysoprase',
  'taleteller', 'effeteness', 'apathetic', 'postclavicular', 'radialia',
  'guimpe', 'succeedingly', 'Lum', 'overhumanize', 'winnelstrae',
  'unfloor', 'nonperishing', 'lovelessly', 'Rebeccaism', 'dobbing',
  'epileptogenic', 'imperialization', 'sniffle', 'swanwort', 'necremia',
  'subbranchial', 'octogynious', 'mystagogy', 'cavalry', 'sclerized',
  'relower', 'latheron', 'trimetrical', 'crackmans', 'oxyrhine',
  'beastling', 'trackman', 'unheler', 'necessitude', 'hypocarpium',
  'intertriglyph', 'Quaitso', 'poker', 'innumerous', 'reassay',
  'turbinated', 'collins', 'misderive', 'anticyclic', 'diplocardiac',
  'pavonated', 'perithyroiditis', 'geisha', 'suppressor', 'gametogony',
  'whyfor', 'Kuneste', 'emu', 'anoxemic', 'overrapture', 'dearworthiness',
  'typical', 'isolability', 'cheesemonger', 'conduplicate', 'enervator',
  'prideless', 'Soja', 'oreophasine', 'Bilin', 'acanthopod', 'iconoscope',
  'dispensingly', 'coleopteran', 'thoracoscope', 'trump', 'azofication',
  'gentisein', 'nigglingly', 'monotrematous', 'vota', 'mesopleuron',
  'encephalomalacosis', 'demean', 'fesswise', 'coecal', 'overdosage',
  'nourishingly', 'pluriflagellate', 'conformably', 'podothecal', 'hamingja',
  'calomorphic', 'unejected', 'eristical', 'pseudofeverish', 'duckwing',
  'revealed', 'cleaning', 'ricinelaidic', 'cononintelligent', 'Sidalcea',
  'megalosplenia', 'noncrustaceous', 'inswept', 'pennyworth', 'pitcherlike',
  'crystallography', 'phobic', 'Eldred', 'encolor', 'barkey', 'Timonize',
  'undevoted', 'blepharoplasty', 'proselytize', 'impending', 'triacid',
  'thallogenous', 'coreflexed', 'tubuliferan', 'onflowing', 'genioglossi',
  'malcultivation', 'chlorometer', 'ransom', 'stereoplasm', 'quacksalver',
  'asiento', 'Slavey', 'kuttab', 'centauromachia', 'distributee', 'forged',
  'coberger', 'bravado', 'contortioned', 'producership', 'splanchnesthetic',
  'strangletare', 'reversability', 'Casuarinaceae', 'disquietly', 'mobsman',
  'mistful', 'bureaucracy', 'miscarriage', 'Huma', 'manufacture',
  'twitteration', 'hyperpyrexial', 'gildable', 'twinkledum', 'dolmen',
  'trachyphonous', 'unpreventable', 'Avicenniaceae', 'Viperoidea', 'bemirror',
  'interbank', 'interdictive', 'betterly', 'tribunate', 'exteroceptor',
  'belemnid', 'discontiguousness', 'skimmerton', 'aldermancy', 'estrepe',
  'nondisclosure', 'irreformable', 'diatropism', 'scleromeninx', 'spithame',
  'Astropecten', 'pommee', 'puerperalism', 'anaerobiont', 'disjointedness',
  'comart', 'hyperanabolic', 'scholaptitude', 'houseboating', 'stadion',
  'hyperexcitability', 'unbetoken', 'Amanitopsis', 'duction', 'minimize',
  'visionmonger', 'infracortical', 'histamine', 'pluviometrical', 'wail',
  'euhemerize', 'fingerprint', 'nematozooid', 'nonstudent', 'outport',
  'athericerous', 'Arthuriana', 'Brahmanistic', 'victless', 'steelification',
  'phraseologist', 'synonymous', 'vocular', 'moisture', 'albumean',
  'sheldapple', 'mysel', 'Languedocian', 'ironical', 'unancient', 'rabitic',
  'unexcrescent', 'tonguecraft', 'revulsion', 'learnedly', 'officerhood',
  'flatulence', 'tubiporous', 'gignitive', 'archpatron', 'deliveryman',
  'russety', 'pseudoencephalitic', 'electrostatics', 'Edith', 'septangular',
  'noop', 'subrhomboidal', 'crowdedness', 'lecyth', 'hemigeusia',
  'afterhold', 'verticillary', 'gimcrackery', 'Cetonia', 'Binitarian',
  'ureal', 'sympathizing', 'bocardo', 'unrustling', 'dragsman', 'Hunyak',
  'infusibility', 'snowcap', 'Pernettia', 'definitive', 'unconceited',
  'unlid', 'underbury', 'creasy', 'amatrice', 'violable', 'hailse',
  'expansionist', 'interluder', 'Snohomish', 'glaister', 'unsprouting',
  'semantological', 'penumbral', 'filefish', 'plumagery', 'drail',
  'immethodic', 'Acalypha', 'Hexagynia', 'hydrostat', 'sylphish',
  'semuncia', 'sixhynde', 'unprosaic', 'lamblike', 'postrubeolar',
  'tempestuousness', 'seemless', 'addiment', 'equilibrize', 'bandiness',
  'unscotch', 'insphere', 'myeloblastic', 'unbrookable', 'eccentrate',
  'multihearth', 'buckwasher', 'racketeer', 'hazel', 'frugivorous',
  'jugation', 'Thebaic', 'wonting', 'aliturgic', 'vedika', 'enumerate',
  'nonexistent', 'rudderstock', 'cognation', 'unpinched', 'verminproof',
  'Kieffer', 'unyieldingness', 'unchiseled', 'Clupeodei', 'satyr',
  'outquestion', 'oviparous', 'Leptotyphlops', 'thoracodorsal', 'Memphite',
  'matronage', 'dentatocrenate', 'brimmingly', 'bingey', 'Wakore',
  'Tagakaolo', 'enclaret', 'gliderport', 'hurr', 'unfrankly', 'Baianism',
  'sandy', 'noncombining', 'carpingly', 'perverseness', 'rip', 'entitle',
  'brakeless', 'Franklinian', 'sulfantimonide', 'biscacha', 'Isiacal',
  'pilferingly', 'tucky', 'pilfering', 'vitrotype', 'isolative', 'Algieba',
  'Hyolithes', 'xanthoprotein', 'impudent', 'pollinigerous', 'imaginer',
  'underlinen', 'unadornable', 'scelotyrbe', 'scratchwork', 'unread',
  'supersensualism', 'exfoliatory', 'docket', 'dysarthrosis', 'invaginable',
  'nonrefrigerant', 'aumrie', 'pantle', 'Trisagion', 'antipatheticalness',
  'snowbreak', 'uninfluentiality', 'unicornlike', 'methylsulfanol',
  'melongena', 'megaphotography', 'untempested', 'slackage', 'retiform',
  'counterexaggeration', 'breastweed', 'thermotaxis', 'shootboard',
  'bituminization', 'wordily', 'rocambole', 'styptical', 'interpolation',
  'abreast', 'resounding', 'officeless', 'deepening', 'slideproof', 'rookish',
  'nontimbered', 'neurohypnology', 'meece', 'phytophysiology', 'plethory',
  'postcoxal', 'anatomicophysiologic', 'unatoned', 'recollected', 'margent',
  'autoallogamy', 'retractibility', 'monosulfone', 'unpsychic', 'swank',
  'unprofessed', 'Tantalic', 'stickle', 'cocarboxylase', 'unwhistled',
  'ovateconical', 'lancewood', 'supracentenarian', 'pretelephonic',
  'mandriarch', 'chondroendothelioma', 'liftless', 'subclaim', 'catenate',
  'thema', 'unangelical', 'leadiness', 'valuelessness', 'debituminization',
  'numskulledness', 'caustically', 'zoodynamic', 'sexennially', 'uncrystaled',
  'stocktaker', 'gainsayer', 'lilacthroat', 'phrenosinic', 'liveness',
  'unweld', 'copolymer', 'utrubi', 'gerenuk', 'adfluxion', 'jingoist',
  'gastrosplenic', 'introspectional', 'alphorn', 'daftly', 'Xiphosurus',
  'Eudora', 'dogfall', 'hemiramph', 'craver', 'merogamy', 'hilltop',
  'archmonarchist', 'palewise', 'spectacular', 'circumambience', 'breastwork',
  'multiplane', 'unattributed', 'trinomialist', 'whereness', 'hawbuck',
  'bronzewing', 'unfabulous', 'remigrant', 'loy', 'sulphantimonious',
  'zygodactylic', 'pulleyless', 'nifling', 'metrorrhagic', 'condemnable',
  'bejuggle', 'kylite', 'unfactored', 'subrogate', 'coruscant',
  'showable', 'ophiasis', 'revictorious', 'carlin', 'expansional',
  'journalizer', 'observatory', 'pursuitmeter', 'subchorionic', 'molary',
  'blub', 'unchangedness', 'garran', 'suitability', 'septenary', 'woak',
  'Zygnemaceae', 'noncompetent', 'periphysis', 'flam', 'chinawoman',
  'dactylioglyphy', 'outlaw', 'preachification', 'trochilus', 'descale',
  'neurohypnotic', 'sexualism', 'matranee', 'chromaticity', 'Herbartianism',
  'scapethrift', 'nectarium', 'bromelin', 'institutionalism', 'Cinchona',
  'slighted', 'muzzle', 'introducement', 'osteomyelitis', 'victordom',
  'granitize', 'glossologist', 'decolorimeter', 'magniloquently',
  'peptonaemia', 'cacomorphosis', 'orthography', 'phalera', 'montane',
  'dyeleaves', 'subendocardial', 'Cistercian', 'bryological', 'rectangular',
  'formaldehydesulphoxylate', 'infraocclusion', 'unoppressed', 'dairymaid',
  'r', 'vasostimulant', 'pachyodont', 'luncheoner', 'garibaldi',
  'hypertrophy', 'counternarrative', 'metascutellar', 'Keftiu', 'petrie',
  'torchwood', 'gnostically', 'unroot', 'fig', 'Nemalionales',
  'profiting', 'vagaristic', 'lormery', 'gurgoyle', 'intercurl', 'evoke',
  'diabrosis', 'reactuate', 'gluma', 'prostheca', 'fernshaw', 'barras',
  'Filaria', 'domnei', 'punctule', 'appropinquity', 'renavigate',
  'unsafeguarded', 'tyrotoxicon', 'Vaseline', 'incalculable', 'outsound',
  'logos', 'cicatrisive', 'hypertetrahedron', 'gopher', 'bathymetrically',
  'allelomorph', 'intransigentism', 'petalite', 'removal', 'cleistothecium',
  'sulphohydrate', 'cloverroot', 'fossilism', 'Manacus', 'Lophophorinae',
  'predispositional', 'pachydermatocele', 'coroneted', 'fivefoldness',
  'matronship', 'suggest', 'intraimperial', 'bigamic', 'introsuction',
  'assailer', 'petrolific', 'beachcomber', 'nonconformer', 'antiattrition',
  'fashiousness', 'scincoid', 'fjeld', 'subgeneric', 'uranoscope', 'purree',
  'foggy', 'velvety', 'comprehensor', 'equilocation', 'impostorship',
  'unskillful', 'cervicaprine', 'styceric', 'Corinna', 'paleotechnic',
  'propolis', 'marquis', 'fulvid', 'monumental', 'noneastern', 'lapped',
  'wyliecoat', 'moldwarp', 'pyloroscopy', 'congruously', 'mathematic',
  'dorsiduct', 'uncriticisingly', 'pretemperate', 'epigene', 'battleward',
  'hematocrit', 'trochitic', 'scythestone', 'pachydermatously',
  'equiangle', 'overpour', 'underreckon', 'trionychoid', 'aortarctia',
  'geophagia', 'hagiography', 'nub', 'simar', 'gourmet', 'dont',
  'islandy', 'mothersome', 'unballasted', 'coloradoite', 'quadrifoliate',
  'mugient', 'fipple', 'tapaculo', 'Hyphaene', 'wirble', 'ammodytoid',
  'hydrotherapy', 'Marattiaceae', 'miscellaneousness', 'Esselenian',
  'viatometer', 'demephitize', 'trophophorous', 'extort', 'namesake',
  'cutaneal', 'therewhile', 'testing', 'Treculia', 'archworkmaster',
  'nonattestation', 'chastely', 'Marathonian', 'earsore', 'amende',
  'navette', 'unscanted', 'quashy', 'noncontradiction', 'berthing',
  'reck', 'graze', 'foil', 'antipragmatist', 'uptree', 'recolonize',
  'dianodal', 'gyromagnetic', 'subpanel', 'rumblegarie', 'hermitism',
  'Anglify', 'Cycadofilicales', 'townland', 'chlorophenol', 'mouseproof'
]


def random_words(count=100, supplemental_word_file_path='/usr/share/dict/words'):
  """Return a random selection of count words from WORDS_1K.

  Include words from file if number of words requested is more than available in
  WORDS_1K.

  """
  if count <= len(WORDS_1K):
    return random.sample(WORDS_1K, count)
  with codecs.open(supplemental_word_file_path, 'r', 'utf-8') as f:
    supplemental_word_list = f.read().splitlines()
  supplemental_word_list.extend(WORDS_1K)
  return random.sample(supplemental_word_list, count)
