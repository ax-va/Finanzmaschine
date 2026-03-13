from finanzmaschine.catalog import registry

instrument = registry.by_isin("GB00BLD4ZM24")
print(instrument)