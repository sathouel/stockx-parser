
browse_products_query = '''
    query Browse(
    $category: String
    $filters: [BrowseFilterInput]
    $query: String
    $sort: BrowseSortInput
    $page: BrowsePageInput
    $currency: CurrencyCode
    $country: String!
    $market: String
    ) {
    browse(
        category: $category
        filters: $filters
        query: $query
        sort: $sort
        page: $page
    ) {
        results {
        edges {
            objectId
            node {
            ... on Product {
                ...ProductDetailsFragment
                ...ProductTraitsFragment
                market(currencyCode: $currency) {
                ...MarketFragment
                }
            }
            ...BidButtonFragment
            }
        }
        pageInfo {
            limit
            page
            pageCount
            queryId
            queryIndex
            total
        }
        }
        query
    }
    }

    fragment ProductDetailsFragment on Product {
    id
    urlKey
    title
    brand
    description
    model
    productCategory
    media {
        thumbUrl
    }
    }

    fragment ProductTraitsFragment on Product {
    productTraits: traits {
        name
        value
    }
    }

    fragment MarketFragment on Market {
    currencyCode
    bidAskData(market: $market, country: $country) {
        lowestAsk
        numberOfAsks
        highestBid
        numberOfBids
        lastHighestBidTime
        lastLowestAskTime
        highestBidSize
        lowestAskSize
    }
    salesInformation {
        lastSale
        lastSaleDate
        salesThisPeriod
        salesLastPeriod
        changeValue
        changePercentage
        volatility
        pricePremium
        annualHigh
        annualLow
        salesLast72Hours
    }
    deadStock {
        sold
        averagePrice
    }
    }

    fragment BidButtonFragment on Product {
    id
    variants {
        id
        hidden
        traits {
        size
        }
        sizeChart {
        baseSize
        baseType
        displayOptions {
            size
            type
        }
        }
        market(currencyCode: $currency) {
        ...MarketFragment
        }
    }
    }
'''

browse_bids_asks_query = '''
    query Browse(
    $category: String
    $filters: [BrowseFilterInput]
    $query: String
    $sort: BrowseSortInput
    $page: BrowsePageInput
    $currency: CurrencyCode
    $country: String!
    $transactionType: TransactionType  
    $limit: Int
    ) {
    browse(
        category: $category
        filters: $filters
        query: $query
        sort: $sort
        page: $page
    ) {
        results {
        edges {
            objectId
            node {
            ... on Product {
                id
                urlKey
                market(currencyCode: $currency) {
                ...MarketPriceLevelsFragment
                }
            }
            }
        }
        pageInfo {
            limit
            page
            pageCount
            queryId
            queryIndex
            total
        }
        }
        query
    }
    }

    fragment MarketPriceLevelsFragment on Market {
    priceLevels(
        country: $country
        transactionType: $transactionType
        page: 1
        limit: $limit
    ) {
        edges {
        node {
            count
            ownCount
            amount
            variant {
            id
            traits {
                size
            }
            }
        }
        }
    }
    }
'''

get_product_price_levels_query = '''
query GetProductPriceLevels(
  $productId: String!
  $country: String
  $currencyCode: CurrencyCode
  $transactionType: TransactionType
  $page: Int
  $limit: Int
  $isVariant: Boolean!
) {
  product(id: $productId) @skip(if: $isVariant) {
    id
    market(currencyCode: $currencyCode) {
      ...MarketPriceLevelsFragment
    }
  }
  variant(id: $productId) @include(if: $isVariant) {
    id
    market(currencyCode: $currencyCode) {
      ...MarketPriceLevelsFragment
    }
  }
}

fragment MarketPriceLevelsFragment on Market {
  priceLevels(
    country: $country
    transactionType: $transactionType
    page: $page
    limit: $limit
  ) {
    edges {
      node {
        count
        ownCount
        amount
        variant {
          id
          traits {
            size
          }
        }
      }
    }
  }
}
'''