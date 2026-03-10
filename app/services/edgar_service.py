import requests


class EdgarService:

    BASE_URL = "https://data.sec.gov"

    HEADERS = {
        "User-Agent": "sec-analyzer research@example.com"
    }

    def get_company_submissions(self, cik: str):
        """
        Fetch SEC company submission JSON.
        """

        cik = cik.zfill(10)

        url = f"{self.BASE_URL}/submissions/CIK{cik}.json"

        response = requests.get(url, headers=self.HEADERS)

        response.raise_for_status()

        return response.json()

    def find_10k_for_year(self, submissions: dict, year: int):
        """
        Locate the 10-K filing for a specific year.
        """

        filings = submissions["filings"]["recent"]

        forms = filings["form"]
        accession_numbers = filings["accessionNumber"]
        filing_dates = filings["filingDate"]

        for i, form in enumerate(forms):

            if form != "10-K":
                continue

            filing_year = int(filing_dates[i].split("-")[0])

            if filing_year == year:

                accession = accession_numbers[i].replace("-", "")

                return {
                    "accession": accession,
                    "filing_date": filing_dates[i]
                }

        return None

    def fetch_filing_document(self, cik: str, accession: str):
        """
        Download the filing HTML.
        """

        cik_int = str(int(cik))

        url = f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{accession}/{accession}-index.html"

        response = requests.get(url, headers=self.HEADERS)

        response.raise_for_status()

        return response.text
