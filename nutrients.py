class Vitamins:
    Vitamin_a: InfoItem
    vitamin_b1: InfoItem [thiamin, thiamine]
    vitamin_b2: InfoItem [riboflavin]
    vitamin_b3: InfoItem [niacin]
    vitamin_b5: InfoItem [pantothenic_acid]
    vitamin_b6: InfoItem
    vitamin_h: InfoItem [biotin, vitamin_b7, vitamin_b8]
    vitamin_b9: InfoItem [folate]
    vitamin_b12: InfoItem
    vitamin_c: InfoItem
    vitamin_d2: InfoItem
    vitamin_d3: InfoItem
    vitamin_e: InfoItem
    vitamin_k1: InfoItem
    vitamin_k2: InfoItem
    choline: InfoItem


class Macronutrient:
    fat: InfoItem
    saturated: InfoItem
    monounsaturated: InfoItem
    polyunsaturated: InfoItem
    carbohydrate: InfoItem
    sugar: InfoItem
    fibre: InfoItem
    protein: InfoItem
    salt: InfoItem
    omega_3: InfoItem
    omega_3_ala: InfoItem
    omega_6: InfoItem


class Minerals:
    postassium: InfoItem
    chloride: InfoItem
    calcium: InfoItem
    phosphorus: InfoItem
    magnesium: InfoItem
    iron: InfoItem
    zinc: InfoItem
    copper: InfoItem
    manganese: InfoItem
    selenium: InfoItem
    chromium: InfoItem
    molybdenum: InfoItem
    sodium: InfoItem
    iodine: InfoItem


class NutrientInfo:
    def __init__(self):
        energy: GeneralItem(EnergyUnit)
        cholesterol: InfoItem
        MCT: InfoItem
        trans_fat: InfoItem
        # lycopene: InfoItem -- no effect
        # lutein: InfoItem -- no effect
        # zeaxanthin: InfoItem -- unproven effects


class FoodItem(object):
    pass


# TODO: implement html source download
def interactive():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('site', type=str,
                        help='website to download files from')
    parser.add_argument('-d', '--dir', default=Path('.'), type=Path,
                        help='directory to save files in')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-r', '--root', default=None, type=str,
                       help='url of the toplevel which should not be left')
    group.add_argument('-l', '--local', action='store_true',
                       help='alternative to root, sets root to value of site')
    parser.add_argument('-i', '--ignore_root', action='store_true',
                        help=('ignore toplevel when deciding '
                              'whether to download a particular pdf '
                              '(toplevel only used for recursive walk)'))
    parser.add_argument('-e', '--element', default="#content", type=str,
                        help='maximum number of links to follow')
    parser.add_argument('-m', '--max_depth', default=20, type=int,
                        help='maximum number of links to follow')
    parser.add_argument('-w', '--logfile', default=Path("log.txt"), type=Path,
                        help="name of the logfile")
    args = parser.parse_args()

    selection_filter = (lambda url: url.path.endswith(".pdf"))
    root = bind(args.root if not args.local else args.site, urlparse)
    if root and not args.ignore_root:
        selection_filter = all_fn(selection_filter,
                                  rpartial(urlstartswith, root))

    links = get_links(urlparse(args.site),
                      element=args.element,
                      selection_filter=selection_filter,
                      recurse_filter=(partial(subsite, root) if root
                                      else (lambda _: True)),
                      depth=args.max_depth)
    logs = errors, non_pdfs, already_present = save_files(links, args.dir)
    num_links = sum(map(len, links.values()))
    print(f"Downloaded {num_links - sum(map(len, logs))} "
          f"out of {num_links} pdfs to {args.dir} "
          f"({len(already_present)} were already present)")
    print()
    if non_pdfs:
        print(f"There were {len(non_pdfs)} non-pdf responses:")
        for response in non_pdfs:
            print(f"{response.url}: {response.headers['Content-Type']}")
    else:
        print("There were no non-pdf responses.")
    print()
    if errors:
        print(f"There were {len(errors)} errors:")
        for error in errors:
            print(f"{error.url}: {error.status_code} [{error.reason}]")
    else:
        print("There were no errors.")


if __name__ == '__main__':
    interactive()
