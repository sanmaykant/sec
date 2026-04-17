from enum import Enum
from edgar import Company, set_identity
from edgar.core import dataclass
from .result import Result

class FetchError(Enum):
    FAILED_TO_FETCH = "Failed to fetch filing"
    FAILED_TO_PARSE = "Failed to parse fetched filing"
    FAILED_TO_PARSE_SECTION = "Section not found or failed to parse section"

@dataclass
class Filing:
    ticker: str
    year: int
    filing: str
    section: str

    def __getitem__(self, key):
        return getattr(self, key)

def fetch_filing(
        ticker: str,
        year: int,
        form: str = "10-K",
        section_name: str = "part_i_item_1a") -> Result[Filing, FetchError]:
    set_identity("your.name@example.com")

    x = Company(ticker)
    filings = x.get_filings(form=form, year=year)

    if len(filings) == 0:
        Result.fail(FetchError.FAILED_TO_FETCH)

    filing = filings[0]
    parsed_filing = filing.parse()

    if parsed_filing is None:
        Result.fail(FetchError.FAILED_TO_PARSE)

    if section_name not in parsed_filing.sections:
        Result.fail(FetchError.FAILED_TO_PARSE_SECTION)

    raw_section = parsed_filing.get_sec_section(section_name)
    return Result.ok(Filing(ticker=ticker,
                            year=year,
                            section=section_name,
                            filing=raw_section))
