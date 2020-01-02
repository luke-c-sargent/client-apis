import logging
from anvil.gen3_auth import Gen3TerraAuth
from anvil.terra import whoami
from gen3.submission import Gen3Submission


def test_gen3_terra_auth(terra_auth_url, user_email, gen3_endpoint):
    """Validates retrieving access_token and passing to gen3."""
    # create default authentication
    auth = Gen3TerraAuth(terra_auth_url=terra_auth_url, user_email=user_email)

    submission_client = Gen3Submission(gen3_endpoint, auth)
    logging.debug('attempting retrieval of graphql schema')
    assert submission_client.get_graphql_schema(), "MUST be able to access open url"
    logging.debug('OK retrieval of graphql schema')

    logging.debug('attempting retrieval of programs list')
    programs = submission_client.get_programs()
    assert len(programs) > 0, f'MUST have at least one program {gen3_endpoint}'
    logging.debug(programs)

    logging.debug('attempting retrieval of project list')
    # parse program name from links
    programs = [p.split('/')[-1] for p in programs['links']]
    for program in programs:
        projects = submission_client.get_projects(program)
        assert len(projects) > 0, f'MUST have at least one project {program}'
    logging.debug(f'OK: Authenticated from {auth._terra_auth_url} to {gen3_endpoint} projects: {projects}')


def test_terra_whoami(user_email):
    me = whoami()
    logging.debug(me)
    assert me == user_email, "MUST have terra identity"
