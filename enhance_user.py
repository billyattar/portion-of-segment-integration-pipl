import analytics
from piplapis.search import SearchAPIRequest


def enhance_segment_user(user):
    resp = SearchAPIRequest(email=user.email,
                            first_name=user.first_name,
                            last_name=user.last_name,
                            show_sources='matching').send()

    if resp.warnings:
        logger.warning("Got {} warnings for Pipl enhancement".format(len(resp.warnings)))
        for warning in resp.warnings:
            logger.warning(warning)

    if resp.person:
        traits = {}
        
        if person.dob:
            traits['age'] = person.dob.age
            
        if person.educations:
            traits['degree'] = person.educations[0]._display

        if person.languages:
            traits['language'] = person.languages[0]._display

        if person.gender:
            traits['gender'] = person.gender.display

        for p in person.phones:
            if p.type == 'work_phone':
                traits['phone'] = p.display_international

        if person.names and (not user.first_name or not user.last_name):
            name = person.names[0]
            traits['firstName'] = name.first
            traits['lastName'] = name.last

        if person.jobs:
            job = person.jobs[0]
            traits['Job Title'] = job.title
            traits['Organization'] = job.organization
            traits['Industry'] = job.industry

        if person.emails:
            query_md5 = resp.query.emails[0].address_md5
            match_email = ([e for e in person.emails if e.address_md5 == query_md5] or [None])[0]
            if match_email:
                traits['Disposable Email'] = 'Yes' if match_email.disposable else 'No'
                traits['Email Provider'] = 'Public' if match_email.email_provider else 'Work'

        domain_names = [
            ('linkedin.com', 'LinkedIn'),
            ('facebook.com', 'Facebook'),
            ('plus.google.com', 'G+'),
            ('twitter.com', 'Twitter'),
            ('pinterest.com', 'Pinterest'),
            ('reddit.com', 'Reddit'),
        ]

        sources_by_domain = resp.group_sources_by_domain()
        for domain, name in domain_names:
            sources = sources_by_domain.get(domain, [])
            for src in sources:
                if src.usernames:
                    traits['{} Username'.format(name)] = src.usernames[0].content
                    if src.user_ids:
                        traits['{} User ID'.format(name)] = src.user_ids[0].content.split('@')[0]
                    break
            for src in sources:
                if 'avatar' not in traits and src.images:
                    traits['avatar'] = src.images[0].url

        if 'avatar' not in traits and person.images:
            traits['avatar'] = person.images[0].url

        analytics.identify(user.email, traits)
