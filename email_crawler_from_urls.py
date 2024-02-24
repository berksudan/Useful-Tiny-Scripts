"""
Module to scrape email addresses from HTML content, including obfuscated email addresses.

Functions:
- escape_raw_parantheses(a_str: str) -> str
- deobfuscate_html(html_text: str) -> str
- unhide_email(hidden_email: str) -> str
- scrape_emails(html_text: str, debug_mode: bool) -> Set[str]
- main()
- test()

Classes:
- None
"""

import re
import urllib.request
from itertools import product
import base64
from typing import Set
import html

RAW_URLS = """
https://webarchiv.typo3.tum.de/EI/ls-rcs/en/rcs/staff/mueller-gritschneder/index.html
https://webarchiv.typo3.tum.de/EI/ls-rcs/en/rcs/staff/schmoeller/index.html
https://webarchiv.typo3.tum.de/EI/ls-rcs/en/rcs/staff/balszun/index.html
https://webarchiv.typo3.tum.de/EI/ls-rcs/en/rcs/staff/geier/index.html
https://webarchiv.typo3.tum.de/EI/ls-rcs/en/rcs/staff/heitmann-nils/index.html
https://webarchiv.typo3.tum.de/EI/ls-rcs/en/rcs/staff/gfuellner/index.html
"""

TLD_SET = {
    "cologne", "jot", "nowtv", "site", "hangout", "gratis", "xn--jlq480n2rg", "uk", "guge", "ge", "xn--mgbbh1a71e", "sex", "africa", "basketball", "xn--eckvdtc9d", "cfa", "xn--czr694b", "insure", "xn--90ae", "pictures", "aeg", "walter", "emerck", "xn--jvr189m", "bb", "bd", "star", "theater", "luxury", "vodka", "football", "desi", "nr", "poker", "sx", "jnj", "marshalls", "praxi", "ga", "financial", "frontier", "xn--j6w193g", "man", "redstone", "tci", "trust", "aq", "hosting", "wanggou", "mma", "actor", "bio", "tn", "mp", "gr", "help", "sn", "photo", "cards", "nf", "property", "ping", "abb", "bbva", "bestbuy", "map", "sharp", "equipment", "lefrak", "safety", "lilly", "fujitsu", "digital", "compare", "xn--mgbgu82a", "bmw", "ing", "kr", "press", "contractors", "xn--qxa6a", "marriott", "pt", "blockbuster", "lamborghini", "investments", "af", "prudential", "xn--xkc2dl3a5ee0h", "jpmorgan", "coupon", "tires", "pizza", "xn--80ao21a", "jewelry", "gb", "locus", "xn--vuq861b", "xn--fiqz9s", "pe", "phd", "hdfc", "beats", "xn--4gbrim", "homedepot", "weatherchannel", "beer", "accenture", "jetzt", "xn--fpcrj9c3d", "sony", "flowers", "samsclub", "ky", "inc", "shia", "ni", "bm", "pn", "wine", "lundbeck", "pay", "care", "book", "smile", "aco", "pictet", "sener", "hkt", "nz", "xn--3e0b707e", "webcam", "samsung", "goog", "sina", "asia", "ht", "analytics", "cpa", "live", "trade", "ai", "lipsy", "microsoft", "ng", "yodobashi", "giving", "sport", "imdb", "brussels", "bentley", "xn--mgbtx2b", "kindle", "jprs", "pf", "download", "legal", "eat", "ericsson", "aig", "sew", "lr", "wedding", "democrat", "ruhr", "fashion", "click", "panasonic", "safe", "xn--45brj9c", "madrid", "shell", "melbourne", "schule", "xn--rovu88b", "ifm", "nissay", "abogado", "fox", "coach", "bv", "bike", "qpon", "bbt", "boehringer", "yandex", "kh", "mls", "gift", "temasek", "hot", "xn--cckwcxetd", "racing", "blog", "msd", "info", "xn--l1acc", "ryukyu", "erni", "vacations", "club", "tjmaxx", "locker", "fans", "diet", "xn--wgbh1c", "lc", "mc", "asdy", "show", "rocks", "walmart", "ooo", "villas", "auction", "shoes", "nyc", "cisco", "nab", "ax", "meme", "pk", "jaguar", "stada", "pharmacy", "bms", "auspost", "navy", "istanbul", "thd", "osaka", "memorial", "song", "host", "xn--j1amh", "in", "weibo", "app", "xyz", "xn--xkc2al3hye2a", "lds", "nissan", "mr", "kia", "menu", "origins", "xn--bck1b9a5dre4c", "jm", "stc", "xn--mgb9awbf", "itv", "rest", "cv", "co", "contact", "degree", "ford", "comsec", "hdfcbank", "me", "party", "bzh", "gu", "tunes", "consulting", "diy", "kddi", "is", "ly", "marketing", "green", "rexroth", "lat", "properties", "firmdale", "vip", "film", "norton", "fm", "yachts", "casino", "lego", "cn", "ninja", "xn--fiq228c5hs", "cw", "ist", "aw", "gal", "orange", "ong", "sncf", "cab", "search", "xn--w4r85el8fhu5dnra", "calvinklein", "yamaxun", "xn--d1alf", "hair", "xn--3bst00m", "xn--ngbc5azd", "om", "sky", "ro", "ua", "expert", "george", "iq", "xn--zfr164b", "barclays", "kyoto", "loans", "youtube", "lincoln", "partners", "sandvik", "xn--55qx5d", "sy", "xn--mix891f", "plumbing", "philips", "creditcard", "xn--cck2b3b", "deloitte", "xn--fhbei", "organic", "verisign", "amsterdam", "xn--fjq720a", "buy", "unicom", "vi", "accountant", "domains", "center", "nc", "channel", "joy", "si", "supplies", "prof", "ntt", "lancaster", "ismaili", "realty", "eg", "love", "sj", "jo", "life", "science", "chase", "paris", "jeep", "biz", "zappos", "silk", "gop", "xn--90a3ac", "solar", "attorney", "williamhill", "wow", "td", "toyota", "ubs", "cuisinella", "progressive", "afl", "gallo", "helsinki", "bi", "ftr", "parts", "codes", "ferrari", "network", "barcelona", "cruise", "nl", "seat", "archi", "house", "pw", "travelers", "ggee", "xn--clchc0ea0b2g2a9gcd", "xn--ses554g", "playstation", "accountants", "ltd", "car", "xn--mgbcpq6gpa1a", "ec", "mtn", "cbn", "cipriani", "scb", "mlb", "aramco", "dog", "americanfamily", "ph", "bosch", "ngo", "museum", "sk", "fo", "qa", "tech", "day", "xn--mgbah1a3hjkrd", "barefoot", "zip", "chanel", "xn--t60b56a", "juniper", "win", "xn--mgbc0a9azcg", "xn--80adxhks", "amex", "bargains", "viajes", "asdi", "ibm", "miami", "hr", "su", "makeup", "xn--nqv7f", "obi", "bn", "ao", "voyage", "website", "apartments", "eu", "vc", "xxx", "xn--mk1bu44c", "uz", "wed", "xn--io0a7i", "career", "juegos", "xn--30rr7y", "esq", "whoswho", "world", "agency", "ad", "dabur", "kaufen", "nec", "shopping", "allstate", "autos", "za", "community", "tools", "forsale", "avianca", "wtf", "catholic", "design", "fund", "akdn", "amazon", "estate", "office", "call", "golf", "moto", "tickets", "mv", "drive", "kpn", "ca", "mx", "nagoya", "total", "cl", "engineering", "xn--cg4bki", "berlin", "pramerica", "audi", "bw", "pg", "dance", "flights", "as", "extraspace", "stream", "hitachi", "xn--mgbca7dzdo", "earth", "firestone", "je", "pwc", "abbvie", "xbox", "ltda", "cbre", "xn--45q11c", "oracle", "xn--gk3at1e", "xn--c2br7g", "tushu", "spa", "xn--y9a3aq", "ally", "cz", "xn--qxam", "rugby", "docs", "xn--ygbi2ammx", "bet", "nfl", "xn--j1aef", "viking", "rehab", "bradesco", "tv", "komatsu", "my", "nikon", "shop", "dental", "kiwi", "li", "futbol", "dz", "eco", "net", "ag", "xn--fiq64b", "gripe", "ls", "pr", "gent", "gf", "photography", "rent", "porn", "foundation", "ba", "smart", "you", "dealer", "hughes", "fish", "final", "fun", "cg", "buzz", "gap", "bloomberg", "xn--fzys8d69uvgm", "xn--8y0a063a", "mq", "zone", "io", "sm", "bh", "crs", "xn--vermgensberatung-pwb", "radio", "guru", "it", "tkmaxx", "ps", "mint", "viva", "soccer", "repair", "dubai", "schaeffler", "anquan", "ml", "uno", "cricket", "holdings", "joburg", "xin", "ren", "dhl", "airforce", "circle", "construction", "dclk", "okinawa", "yokohama", "top", "im", "genting", "med", "rich", "gm", "godaddy", "sohu", "durban", "gold", "tz", "tjx", "eus", "icbc", "fk", "airtel", "mh", "xn--mgbayh7gpa", "trading", "bharti", "baseball", "farm", "here", "fan", "by", "sale", "surf", "lt", "xn--mxtq1m", "bot", "fast", "anz", "xn--efvy88h", "rw", "tienda", "barclaycard", "xn--h2brj9c8c", "realestate", "ve", "gp", "amfam", "catering", "fresenius", "guitars", "la", "natura", "olayangroup", "vet", "room", "aarp", "fidelity", "courses", "bar", "dad", "mckinsey", "forum", "comcast", "aol", "ne", "kuokgroup", "media", "tm", "sg", "sucks", "xn--mgbbh1a", "video", "pet", "az", "mobi", "crown", "college", "il", "kids", "place", "cfd", "pm", "lpl", "cloud", "tr", "art", "ae", "cymru", "charity", "xn--kprw13d", "salon", "pioneer", "ie", "homes", "hyatt", "fishing", "online", "rwe", "tiaa", "xn--tiq49xqyj", "immobilien", "vegas", "lv", "canon", "olayan", "nrw", "technology", "frogans", "na", "bostik", "fire", "zw", "re", "ws", "feedback", "audible", "deals", "abbott", "build", "report", "doctor", "faith", "hamburg", "de", "pa", "epson", "institute", "vin", "xn--b4w605ferd", "coffee", "sydney", "hiv", "pru", "toshiba", "yt", "visa", "py", "homesense", "lifeinsurance", "guide", "at", "wtc", "horse", "xn--vhquv", "tel", "alsace", "ki", "vote", "tab", "sv", "mobile", "loan", "sling", "tf", "direct", "hyundai", "xn--80asehdb", "fido", "tattoo", "global", "condos", "flickr", "next", "auto", "pink", "bbc", "sz", "vlaanderen", "xn--otu796d", "tdk", "sandvikcoromant", "yahoo", "cleaning", "bz", "saxo", "physio", "wales", "gy", "bridgestone", "alibaba", "grocery", "movie", "save", "discount", "st", "versicherung", "xn--2scrj9c", "lotte", "zero", "store", "kp", "tatar", "glass", "bible", "link", "goodyear", "graphics", "irish", "creditunion", "taobao", "xn--mgbab2bd", "lawyer", "xn--mgbai9azgqp6j", "capetown", "alstom", "gq", "kn", "nokia", "xn--1ck2e1b", "th", "tvs", "softbank", "lexus", "email", "monster", "lamer", "moe", "asda", "mo", "republican", "xn--mgbx4cd0ab", "fr", "kw", "sbs", "lplfinancial", "social", "ss", "secure", "shaw", "country", "finance", "exposed", "xn--11b4c3d", "staples", "srl", "dev", "rs", "mg", "netflix", "travel", "vu", "sb", "mov", "xn--42c2d9a", "gl", "pro", "sas", "google", "bo", "kfh", "itau", "adult", "black", "security", "wang", "work", "xn--mgbt3dhd", "dating", "so", "maif", "mn", "london", "xn--wgbl6a", "americanexpress", "diamonds", "realtor", "xn--g2xx48c", "booking", "haus", "tatamotors", "best", "jp", "lgbt", "cc", "us", "hockey", "edu", "supply", "statefarm", "aaa", "gg", "games", "saarland", "review", "pars", "schwarz", "be", "gallery", "xn--gckr3f0f", "florist", "support", "dk", "dupont", "mormon", "icu", "se", "xn--ogbpf8fl", "audio", "fi", "watches", "cern", "market", "cal", "cat", "blackfriday", "school", "dunlop", "delivery", "sbi", "bcn", "food", "blue", "tg", "industries", "gmail", "tw", "company", "bt", "xn--80aswg", "mini", "goo", "bj", "pohl", "abudhabi", "boutique", "virgin", "sap", "xn--flw351e", "xn--mgbpl2fh", "nowruz", "mitsubishi", "vig", "quest", "caravan", "toray", "zuerich", "now", "xn--6frz82g", "kerryproperties", "phone", "asdadel", "living", "xn--p1acf", "au", "baidu", "ferrero", "xn--55qw42g", "taipei", "xn--kcrx77d1x4a", "dentist", "nu", "apple", "camp", "pl", "xn--lgbbat1ad8j", "builders", "space", "business", "associates", "bofa", "gmx", "vn", "bnpparibas", "mit", "xn--gecrj9c", "fit", "able", "reit", "weber", "xn--4dbrk0ce", "agakhan", "tokyo", "omega", "gdn", "directory", "latrobe", "xn--mgba7c0bbn0a", "kz", "guardian", "kitchen", "nico", "express", "dj", "garden", "hk", "bond", "pics", "latino", "university", "sfr", "sexy", "money", "fj", "ee", "engineer", "volvo", "lifestyle", "gw", "xn--80aqecdr1a", "zm", "gn", "tj", "gmbh", "hermes", "do", "mm", "mil", "fail", "asdic", "markets", "clothing", "br", "xn--q7ce6a", "boats", "mu", "xn--mgba3a4f16a", "gh", "ar", "xn--i1b6b1a6a2e", "winners", "moda", "observer", "leclerc", "sh", "bing", "wf", "moscow", "bank", "xn--unup4y", "reise", "ir", "shangrila", "events", "bauhaus", "limited", "xn--3ds443g", "gs", "xn--hxt814e", "skin", "jcb", "nba", "dm", "mt", "enterprises", "productions", "sc", "xn--5su34j936bgsg", "news", "aquarelle", "fairwinds", "otsuka", "xn--nqv7fs00ema", "er", "fitness", "gea", "spot", "xn--imr513n", "rogers", "broadway", "broker", "capitalone", "athleta", "vivo", "voto", "zara", "travelersinsurance", "dish", "plus", "lacaixa", "pub", "deal", "gov", "dtv", "lidl", "target", "xn--kput3i", "prod", "dot", "ups", "xn--90ais", "ricoh", "arte", "cheap", "tk", "cash", "banamex", "watch", "al", "ac", "pin", "llp", "bg", "sa", "ceo", "xn--o3cw4h", "dds", "monash", "ug", "computer", "xn--w4rs40l", "maison", "one", "coupons", "dvag", "tui", "recipes", "gucci", "studio", "bingo", "dell", "hisamitsu", "wien", "immo", "mw", "clinique", "xfinity", "solutions", "xn--c1avg", "redumbrella", "rio", "nexus", "trv", "onl", "wolterskluwer", "meet", "cars", "es", "skype", "honda", "vanguard", "theatre", "kpmg", "xn--5tzm5g", "xn--3hcrj9c", "lighting", "yun", "new", "software", "bayern", "android", "stockholm", "fyi", "management", "cf", "chat", "xn--9et52u", "photos", "baby", "gbiz", "capital", "neustar", "gi", "xn--nyqy26a", "casa", "pid", "xn--3pxu8k", "md", "tirol", "sakura", "hotels", "claims", "xn--mgba3a3ejt", "ke", "town", "run", "xn--d1acj3b", "commbank", "ch", "suzuki", "tl", "kerryhotels", "yoga", "homegoods", "lol", "stcgroup", "ru", "coop", "java", "hsbc", "gd", "style", "uy", "tips", "sr", "am", "page", "tt", "case", "com", "infiniti", "nhk", "ott", "mz", "xn--node", "holiday", "xn--ngbrx", "name", "bom", "rip", "camera", "jll", "xn--vermgensberater-ctb", "today", "id", "kerrylogistics", "healthcare", "cruises", "nike", "seek", "cx", "schmidt", "gay", "international", "weir", "aws", "tax", "hbo", "cam", "health", "swiss", "xn--kpry57d", "va", "reviews", "scot", "dnp", "wme", "abc", "red", "careers", "hm", "clinic", "motorcycles", "chrome", "luxe", "xn--yfro4i67o", "hu", "group", "cba", "xn--45br5cyl", "landrover", "richardli", "read", "talk", "mattel", "taxi", "tc", "author", "boston", "seven", "study", "gives", "xn--pgbs0dh", "xn--6qq986b3xl", "play", "alipay", "aetna", "ma", "promo", "km", "tours", "ads", "limo", "jobs", "game", "law", "arab", "xn--s9brj9c", "xn--qcka1pmc", "pfizer", "ms", "to", "krd", "merckmsd", "hospital", "koeln", "mba", "grainger", "like", "aero", "gifts", "cafe", "academy", "forex", "jmp", "wiki", "axa", "music", "date", "jio", "cooking", "xn--czrs0t", "reisen", "llc", "statebank", "et", "xn--xhq521b", "amica", "tennis", "rsvp", "ci", "gle", "dvr", "azure", "ovh", "kosher", "ski", "army", "cy", "ink", "gallup", "mortgage", "xn--h2brj9c", "fage", "vision", "soy", "post", "org", "men", "ril", "kred", "mtr", "goldpoint", "band", "intuit", "christmas", "discover", "xn--9krt00a", "voting", "data", "open", "vana", "xn--fiqs8s", "ventures", "ice", "uol", "boo", "sd", "xn--54b7fta0cc", "sarl", "quebec", "windows", "protection", "bf", "hotmail", "surgery", "ikano", "mom", "lb", "cyou", "globo", "land", "education", "restaurant", "tmall", "fly", "mango", "nextdirect", "sanofi", "lotto", "got", "datsun", "family", "mk", "scholarships", "gmo", "xn--9dbq2a", "bcg", "ollo", "pccw", "nra", "pnc", "no", "teva", "how", "free", "cool", "shiksha", "clubmed", "xn--tckwe", "cm", "toys", "xn--rvc1e0am3e", "politie", "lanxess", "xn--pssy2u", "ck", "farmers", "bs", "systems", "church", "storage", "netbank", "credit", "hiphop", "beauty", "energy", "airbus", "lease", "tube", "flir", "shouji", "xn--rhqv96g", "frl", "kim", "ieee", "xerox", "cd", "xn--fct429k", "xn--mgbi4ecexp", "eurovision", "prime", "vg", "insurance", "rodeo", "works", "corsica", "kg", "xn--p1ai", "training", "lasalle", "xn--mgberp4a5d4ar", "xn--ngbe9e0a", "gt", "xn--fzc2c9e2c", "exchange", "int", "swatch", "foo", "xn--1qqw23a", "fedex", "lu", "singles", "xihuan", "team", "brother", "cr", "select", "xn--e1a4c", "services", "box", "lk", "ubank", "arpa", "weather", "moi", "chintai", "bid", "ye", "woodside", "delta", "np", "xn--h2breg3eve", "imamat", "allfinanz", "sl", "furniture", "rentals", "cu", "hn", "reliance", "edeka", "xn--czru2d", "xn--mgbaam7a8h", "ipiranga", "xn--q9jyb4c", # pylint: disable=line-too-long
}

EMAIL_REGEX = (
    "([%(local)s][%(local)s.]+[%(local)s]@[%(domain)s.]+\\.(?:%(tlds)s))(?:[^%(domain)s]|$)"
    % {
        "local": "A-Za-z0-9!#$%&'*+\\-/=?^_`{|}~",
        "domain": r"A-Za-z0-9\-",
        "tlds": "|".join(TLD_SET),
    }
)

HIDDEN_AT_SYM = (
    " _at_ ",
    "_at_",
    " (at) ",
    "(at)",
    " (AT) ",
    "(AT)",
    " [at] ",
    "[at]",
    " (@) ",
    "(@)",
    "[@]",
    " [@] ",
    " @ ",
)
HIDDEN_DOT_SYM = (
    " (dot) ",
    "(dot)",
    " [dot] ",
    "[dot]",
    " (.) ",
    "(.)",
    " [.] ",
    "[.]",
    " . ",
)


def escape_raw_parantheses(a_str: str):
    """
    Replace parantheses in the provided string with escape characters.

    :param a_str: The input string
    :return: The modified string with escaped parantheses
    """
    return (
        a_str.replace("(", r"\(")
        .replace(")", r"\)")
        .replace("[", r"\[")
        .replace("]", r"\]")
    )


at_dot_combinations = (
    list(product(HIDDEN_AT_SYM, HIDDEN_DOT_SYM))
    + list(product(["@"], HIDDEN_DOT_SYM))
    + list(product(HIDDEN_AT_SYM, ["."]))
)

hidden_regex = [
    "(\\w+[({1})\\w+]*({0})\\w+({1})\\w+[({1})\\w+]*)".format( # pylint: disable=consider-using-f-string
        escape_raw_parantheses(at),
        escape_raw_parantheses(dot),
    )
    for at, dot in at_dot_combinations
]


def deobfuscate_html(html_text: str):
    """
    Deobfuscate HTML text containing encoded elements like 'atob'

    :param html_text: HTML text to be deobfuscated
    :return: Deobfuscated HTML text
    """

    def unescape(html_text):
        return html.unescape(html_text)

    def replace_atob(matchobj):
        return base64.b64decode(matchobj.groups()[0].encode("utf-8")).decode("utf-8")

    html_text = unescape(html_text)
    html_text = re.sub("atob\\(['\"]([A-Za-z0-9+/]+)['\"]\\)", replace_atob, html_text)
    return html_text


def unhide_email(hidden_email: str) -> str:
    """
    Replace hidden symbols in an email with their actual symbols

    :param hidden_email: Email address containing hidden symbols
    :return: Email address with actual symbols
    """
    for at_sym in HIDDEN_AT_SYM:
        hidden_email = hidden_email.replace(at_sym, "@")
    for dot_sym in HIDDEN_DOT_SYM:
        hidden_email = hidden_email.replace(dot_sym, ".")
    return hidden_email


def scrape_emails(html_text: str, debug_mode: bool) -> Set[str]:
    """
    Look for email addresses in HTML and return them. This includes addresses in the html text, 
    links and even obfuscated email addresses. Currently supports `atob()` and 
    HTML entities obfuscations.

    :return: a set of email addresses found in the HTML
    """
    html_text = deobfuscate_html(html_text)

    hidden = []
    for expr in hidden_regex:
        matches = []
        for i in re.findall(expr, html_text):
            if debug_mode:
                print(">> FOUND HIDDEN EMAIL ADDRESS:", i)
            matches.append(unhide_email(i[0]))
            # matches.append(unhide_email(i))
        # hidden += [unhide_email(i[0]) for i in re.findall(expr, html)]
        hidden += matches

    optimized_html_text = ""
    hidden_str = " " + "<>".join(hidden) + " "
    # for poten_email in re.findall(r'.{1,64}@.{1,255}', html):
    for poten_email in re.findall(r".{1,64}@.{1,255}", html_text + hidden_str):
        optimized_html_text += " " + poten_email
    # extracted_emails = re.findall(EMAIL_REGEX, optimized_html_text) + hidden
    extracted_emails = re.findall(EMAIL_REGEX, optimized_html_text)
    return set(extracted_emails)  # To make the list unique
    # return re.findall(EMAIL_REGEX, optimized_html_text)


def main():
    """
    Main function to extract emails from a list of URLs.
    It prints the URLs along with the extracted email addresses.
    """
    urls = RAW_URLS.strip().split("\n")

    for url in urls:
        with urllib.request.urlopen(url) as response:
            html_text = response.read().decode("utf-8")

        found_emails = scrape_emails(html_text, debug_mode=False)
        if len(found_emails) == 0:
            found_emails = set(["[EMAIL NOT FOUND]"])
        for email in found_emails:
            print(f"{url};{email}")


def test():
    """
    Test function to validate the functionality of email extraction.
    Checks various cases of potential inputs to validate the program.
    """
    cases = [
        {"in_html": "hello@world.com", "correct": "hello@world.com"},
        {"in_html": "hello(AT)world.com", "correct": "hello@world.com"},
        {"in_html": "hello (AT) world.com", "correct": "hello@world.com"},
        {"in_html": "hello (at) world.com", "correct": "hello@world.com"},
        {"in_html": "hello (at) world(dot)com", "correct": "hello@world.com"},
        {"in_html": "hello (at) world (dot) com", "correct": "hello@world.com"},
        {
            "in_html": "prefix (dot) hello (at) world (dot) com",
            "correct": "prefix.hello@world.com",
        },
        {
            "in_html": "prefix.hello (at) world (.) postfix (dot) com",
            "correct": "prefix.hello@world.postfix.com",
        },
        {
            "in_html": "prefix.hello (at) world (.) postfix . com",
            "correct": "prefix.hello@world.postfix.com",
        },
        {
            "in_html": "prefix.hello (at) world.postfix.com",
            "correct": "prefix.hello@world.postfix.com",
        },
        {
            "in_html": "<a href=\".href=atob('bWFpbHRvOmVtYWlsQGV4YW1wbGUuY29t')\">E-Mail</a>",
            "correct": "email@example.com",
        },
        ## ERRORONEOUS ONES, CAN BE IMPROVED IN THE FUTURE
        # {'in_html':'j.asd-ddddf(at)asd(dot)asd(dot)de', 'correct': 'j.asd-ddddf@asd.asd.de'},
        # {'in_html':'j.asd-ddddf(at)asd.asd.de', 'correct': 'j.asd-ddddf@asd.asd.de'},
        # {'in_html':'j.asd-ddddf (at) asd.asd.de', 'correct': 'j.asd-ddddf@asd.asd.de'},
        # {'in_html':'prefix . hello (at) world (dot) com', 'correct': 'prefix.hello@world.com'},
        # {
        #     'in_html':'prefix.hello (at) world (dot) postfix (dot) com',
        #     'correct': 'prefix.hello@world.postfix.com'
        # },
    ]
    for case in cases:
        a_text = r'<html><body><a href="mailto:{0}">email me</a></body></html>'
        x = scrape_emails(a_text.format(case["in_html"]), debug_mode=True)
        assert len(x) == 1
        assert (
            list(x)[0] == case["correct"]
        ), f'Given: {list(x)[0]}, Expected: {case["correct"]}'
    print("[INFO] Test successful!")


if __name__ == "__main__":
    test()
    main()
