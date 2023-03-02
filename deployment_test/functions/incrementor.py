import uuid
from django.core.exceptions import ValidationError
from arches.app.functions.base import BaseFunction
from arches.app.models import models
from arches.app.models.tile import Tile
import json
import logging
from django.db.models import Q
logger = logging.getLogger(__name__)


details = {
    "name": "Incrementor",
    "type": "node",
    "description": "Adds a tile to a newly created instance with an incrementing value",
    "defaultconfig": {"selected_nodegroup": "", "target_node":"", "triggering_nodegroups":[], "starting_value": 0, "last_value":0, "prefix":"", "suffix":""},
    "classname": "IncrementorFunction",
    "component": "views/components/functions/incrementor-function",
    "functionid": "2cc07b0a-adbd-4721-86ce-dad1699caa86"
}

class IncrementorFunction(BaseFunction):

    def post_save(self, tile, request):
        logger.error("TESTESTTESTTESTTEST")
        tile_already_exists = models.TileModel.objects.filter(resourceinstance_id=tile.resourceinstance_id).filter(nodegroup_id=self.config["selected_nodegroup"]).exists()
        print(tile_already_exists)
        if not tile_already_exists:
            try:
                if int(self.config['last_value']) == 0:
                    new_number = str(int(self.config['starting_value']) + int(self.config['last_value']) + 1)
                else:
                    new_number = str(int(self.config['last_value']) + 1)
                print(new_number)
                new_value = new_number
                fn = models.FunctionXGraph.objects.get(Q(function_id="2cc07b0a-adbd-4721-86ce-dad1699caa86"), Q(graph_id=tile.resourceinstance.graph_id))
                fn.config['last_value'] = new_number
                fn.save()
                nodegroup_id = self.config["selected_nodegroup"]
                target_node = self.config['target_node']
                nodegroup = models.NodeGroup.objects.get(pk = nodegroup_id)
                if tile.nodegroup.nodegroupid == nodegroup.nodegroupid:
                    print("FIRST IF !!!!!!!!!!!!!!!")
                    tile.data[target_node] = new_value
                    tile.save()
                    return
                if nodegroup.parentnodegroup_id == tile.nodegroup.nodegroupid:
                    print("SECOND IF !!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    return
                else:
                    print("EHFEHFAEF")
                    tile = Tile.update_node_value(target_node, new_value, nodegroupid=nodegroup_id, resourceinstanceid=tile.resourceinstance_id)
            except Exception:
                logger.exception("The incrementor function is unable to create incremented value")
