from polylogyx.models import DefaultQuery, DefaultFilters, db


def get_all_configs():
    platforms = ["windows", "linux", "darwin"]
    config_data = {}
    for platform in platforms:
        if platform == "windows":
            default_platform_queries_x64 = DefaultQuery.query.filter(DefaultQuery.platform == platform).filter(DefaultQuery.arch == DefaultQuery.ARCH_x64).all()
            default_platform_queries_x86 = DefaultQuery.query.filter(DefaultQuery.platform == platform).filter(DefaultQuery.arch == DefaultQuery.ARCH_x86).all()
            queries_data = {"x64": {default_query.name: default_query.to_dict() for default_query in default_platform_queries_x64}, "x86": {default_query.name: default_query.to_dict() for default_query in default_platform_queries_x86}}

            default_filter_obj_x64 = DefaultFilters.query.filter(DefaultFilters.platform == platform).filter(DefaultFilters.arch == DefaultFilters.ARCH_x64).first()
            default_filter_obj_x86 = DefaultFilters.query.filter(DefaultFilters.platform == platform).filter(DefaultFilters.arch == DefaultFilters.ARCH_x86).first()
            if default_filter_obj_x64:
                default_filter_x64 = default_filter_obj_x64.filters
            else:
                default_filter_x64 = {}
            if default_filter_obj_x86:
                default_filter_x86 = default_filter_obj_x86.filters
            else:
                default_filter_x86 = {}
            filters_data = {
                "x64": default_filter_x64,
                "x86": default_filter_x86}

            config_data[platform] = {"queries": queries_data, "filters": filters_data}
        else:
            default_platform_queries = DefaultQuery.query.filter(DefaultQuery.platform == platform).all()
            queries_data = {default_query.name: default_query.to_dict() for default_query in default_platform_queries}
            default_filter = {}
            default_filter_obj = DefaultFilters.query.filter(DefaultFilters.platform == platform).first()
            if default_filter_obj:
                default_filter = default_filter_obj.filters
            config_data[platform] = {"queries": queries_data, "filters": default_filter}
    return config_data


def get_config_by_platform(platform):
    config_data = {}
    if platform == "windows":
        default_platform_queries_x64 = DefaultQuery.query.filter(DefaultQuery.platform == platform).filter(
            DefaultQuery.arch == DefaultQuery.ARCH_x64).all()
        default_platform_queries_x86 = DefaultQuery.query.filter(DefaultQuery.platform == platform).filter(
            DefaultQuery.arch == DefaultQuery.ARCH_x86).all()
        queries_data = {
            "x64": {default_query.name: default_query.to_dict() for default_query in default_platform_queries_x64},
            "x86": {default_query.name: default_query.to_dict() for default_query in default_platform_queries_x86}}

        default_filter_obj_x64 = DefaultFilters.query.filter(DefaultFilters.platform == platform).filter(
            DefaultFilters.arch == DefaultFilters.ARCH_x64).first()
        default_filter_obj_x86 = DefaultFilters.query.filter(DefaultFilters.platform == platform).filter(
            DefaultFilters.arch == DefaultFilters.ARCH_x86).first()
        if default_filter_obj_x64:
            default_filter_x64 = default_filter_obj_x64.filters
        else:
            default_filter_x64 = {}
        if default_filter_obj_x86:
            default_filter_x86 = default_filter_obj_x86.filters
        else:
            default_filter_x86 = {}
        filters_data = {
            "x64": default_filter_x64,
            "x86": default_filter_x86}

        config_data[platform] = {"queries": queries_data, "filters": filters_data}
    else:
        default_platform_queries = DefaultQuery.query.filter(DefaultQuery.platform == platform).all()
        queries_data = {default_query.name: default_query.to_dict() for default_query in default_platform_queries}
        default_filter = {}
        default_filter_obj = DefaultFilters.query.filter(DefaultFilters.platform == platform).first()
        if default_filter_obj:
            default_filter = default_filter_obj.filters
        config_data[platform] = {"queries": queries_data, "filters": default_filter}
    return config_data


def edit_config_by_platform(platform, filters, queries, arch):
    config_data = {}
    for query in queries:
        if 'status' in queries[query]:
            default_query_obj = DefaultQuery.query.filter(DefaultQuery.platform == platform).filter(DefaultQuery.arch == arch).filter(DefaultQuery.name == query).first()
            if default_query_obj and ('interval' in queries[query]): default_query_obj.update(interval=queries[query]['interval'], status=queries[query]['status'], synchronize_session=False)
            elif default_query_obj: default_query_obj.update(status=queries[query]['status'], synchronize_session=False)
    default_filter_obj = DefaultFilters.query.filter(DefaultFilters.platform == platform).filter(DefaultFilters.arch == arch).first()
    if default_filter_obj:
        if not len(filters)==0:
            default_filter_obj.filters = filters
            default_filter_obj.save()
    config_data[platform] = {"queries": queries, "filters": filters}
    return config_data


def add_config_by_platform(platform, filters, queries, arch):
    for query_key in queries.keys():
        query = DefaultQuery(name=query_key, sql=queries[query_key]['sql'], interval=queries[query_key].get('interval', 3600), platform=platform, arch=arch, version=queries[query_key].get('version', None), description=queries[query_key].get('description', None), value=queries[query_key].get('value', None), removed=queries[query_key].get('removed', False), snapshot=queries[query_key].get('snapshot', True), shard=queries[query_key].get('shard', None), status=queries[query_key].get('status', True))
        db.session.add(query)

    DefaultFilters.create(filters=filters, platform=platform, arch=arch)
    response = {"queries": queries, "filters": filters}
    return response