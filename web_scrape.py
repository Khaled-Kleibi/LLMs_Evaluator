import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

def get_links_from_page(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []

        # Extract all anchor tags and filter links
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('/en/information-and-services/'):
                # Ensure the link is complete
                href = 'https://u.ae' + href
                links.append(href)
            elif href.startswith('https://u.ae/en/information-and-services/'):
                links.append(href)
        
        return links
    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return []

# Recursive function to find all subpages
def find_all_subpages(start_url, visited=None, max_depth=15, depth=0):
    if visited is None:
        visited = set()

    if depth > max_depth:
        return visited

    # Get the links from the start page
    links = get_links_from_page(start_url)
    subpages = []

    for link in links:
        if link not in visited:
            visited.add(link)
            print(f"Found link: {link}")
            subpages.append((link, depth + 1))

    # Use ThreadPoolExecutor for concurrent requests
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(find_all_subpages, link, visited, max_depth, depth + 1) for link, depth in subpages]
        for future in futures:
            future.result()

    return visited

# Save links to a text file
def save_links_to_file(links, filename):
    with open(filename, 'w') as file:
        for link in links:
            file.write(f"{link}\n")
    print(f"Links saved to {filename}")


main_url = 'https://u.ae/en/information-and-services'
all_links = find_all_subpages(main_url)

save_links_to_file(all_links, 'scraped_links.txt')
