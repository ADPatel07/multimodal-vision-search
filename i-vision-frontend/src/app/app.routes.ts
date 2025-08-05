import { Routes } from '@angular/router';
import { DetailCardComponent } from './detail-card/detail-card.component';
import { SearchBarComponent } from './search-bar/search-bar.component';
import { AddObjectComponent } from './add-object/add-object.component';
import { HomePageComponent } from './home-page/home-page.component';

export const routes: Routes = [
    {path:"", component: SearchBarComponent},
    {path:"home", component: SearchBarComponent},
    {path:"add", component:AddObjectComponent},
    {path:"details", component:DetailCardComponent}
];
