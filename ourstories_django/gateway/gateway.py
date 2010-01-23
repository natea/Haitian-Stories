from pyamf.remoting.gateway.django import DjangoGateway
import ourstories_django.flv.views as flv_views


services = {
    
    # our stories flv recorder services
    'flv.ping': flv_views.ping,
    'flv.getId': flv_views.get_id, 
    'flv.getIdSig': flv_views.get_id_sig, 
    'flv.setStatus': flv_views.set_status, 
    'flv.setStatusType': flv_views.set_status_type, 
    'flv.linkFlvToStory': flv_views.link_flv_to_story, 
    'flv.dtrace': flv_views.dtrace, 

}

mainGateway = DjangoGateway(services)
